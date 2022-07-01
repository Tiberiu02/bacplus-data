import codecs		
import os, sys
import json
import unidecode

data_dot_gov = False

jcode = {}
jcode.update([x.split(',') for x in open("meta/coduri-judete.txt", "r", encoding="utf-8").read().split('\n') if len(x)])

an = 0

jdecode = {}
for (code, j) in jcode.items():
	jdecode[unidecode.unidecode(j).upper()] = code
	jdecode[unidecode.unidecode(j)] = code
	jdecode[j.upper()] = code
	jdecode[j] = code

class Dataset:
	data = []

	def __init__(self):
		pass;

	def read(self, data_path, meta_path, debug_mode = True):
		# Read SIIIR & SIIRUES high school codes
		siiir, sirues = {}, {}
		if data_dot_gov:
			for e in open("meta/siiir.csv", "r", encoding="utf-8").read().split('\n'):
				a = e.split('\t')
				if (len(a) > 6):
					siiir[a[1]] = [a[2], jdecode[unidecode.unidecode(a[6]).replace("MUNICIPIUL ", "").replace(" ", "-")]]
			for e in open("meta/sirues.csv", "r", encoding="utf-8").read().split('\n'):
				a = e.split('\t')
				if (len(a) > 4):
					sirues[a[3]] = [a[2], jdecode[unidecode.unidecode(a[1]).replace("MUNICIPIUL ", "").replace(" ", "-")]]
			
		# Read input structure (field names & types)
		a_dict, a_names, a_types = {}, [], []
		for e in open(meta_path, "r", encoding="utf-8").read().split('\n'):
			a = e.split('\t')
			if len(a) == 2 and len(a[0]) and len(a[1]):
				a_dict[a[0]] = a[1]
				a_names.append(a[0])
				a_types.append(a[1])
		print("Loaded %d attributes" % (len(a_dict)))
		if debug_mode:
			for n, t in a_dict.items():
				print("%s(%s)" % (n, t))
	
		# Read & clean input
		raw = codecs.open(data_path, "r", encoding='utf-8').read()
		raw = raw.upper()
		raw = raw.replace("Ăˇ", "Á")
		raw = raw.replace("Ă©", "É")
		raw = raw.replace("Ĺ‘", "Ő").replace("Ă¶", "Ö").replace("Ăł", "Ó")
		raw = raw.replace("â€™", "'").replace("Â€™", "'").replace("''", '"').replace(",,", '"').replace("'", '"').replace("„", '"').replace("”", '"').replace("’", '"').replace('""', '"')
		raw = unidecode.unidecode(raw)
		ix = raw.find("€")
		print(raw[ix - 100 : ix + 100])
		print(sorted(set(raw)))

		# Parse input
		ignored = 0
		ign = []
		print(str(an-1) + "-" + str(an))
		for e in raw.replace("'", '"').split('\n'):
			entry = {}
			for ix, a in enumerate(e.split('\t')):
				if len(a) == 0:
					continue
				if ix >= len(a_types):
					print(e.split('\t'))
				if a_types[ix] == "num":
					try:
						entry[a_names[ix]] = float(a)
					except:
						pass
				elif a_types[ix] == "str":
					entry[a_names[ix]] = a.strip()
			
			# Fix adjust adata from data.gov.ro
			if data_dot_gov and len(entry) > 0:
				# Compute final grades
				for x in ["lr", "lm", "do", "da"]:
					if x + "_contestatie" in entry:
						entry[x + "_final"] = entry[x + "_contestatie"]
					elif x + "_initial" in entry:
						entry[x + "_final"] = entry[x + "_initial"]
				# Load school data from siiir/sirues code
				if "siiir" in entry and entry["siiir"] in siiir:
					entry["liceu"] = siiir[entry["siiir"]][0]
					entry["judet"] = siiir[entry["siiir"]][1]
				elif "sirues" in entry and entry["sirues"] in sirues:
					entry["liceu"] = sirues[entry["sirues"]][0]
					entry["judet"] = sirues[entry["sirues"]][1]
				else:
					ign.append(entry["siiir"])
					ignored += 1
					continue
				# Compute previuos promotion
				if "promotie" not in entry:
					print(len(self.data))
				entry["promotie_anterioara"] = "NU" if entry["promotie"] == (str(an-1) + "-" + str(an)) else "DA"
				entry["liceu"] = entry["liceu"].replace("â€™", "'").replace("''", '"').replace(",,", '"').replace("'", '"').replace("„", '"').replace("”", '"').replace("’", '"').upper()
				entry["liceu"] = unidecode.unidecode(entry["liceu"])
					
			if len(entry) > 0:
				self.data.append(entry)
		
		print("Loaded %d entries" % (len(self.data)))
		print("Ignored schools for %d entries" % ignored)
		print("Num ignored schools: %d" % len(set(ign)))
		if len(set(ign)) > 0:
			print(set(ign))
		if debug_mode:
			print("Printing first entry:")
			print(self.data[0])
	
	def corel_str_str(self, a1, a2):
		cnt = {}
		f = {}
		for e in self.data:
			if not a1(e) or not a2(e):
				continue
			if a1(e) not in cnt:
				cnt[a1(e)] = 0
				f[a1(e)] = {}
			cnt[a1(e)] += 1
			if a2(e) not in f[a1(e)]:
				f[a1(e)][a2(e)] = 0
			f[a1(e)][a2(e)] += 1
		
		ans = ""
		for n1, c1 in cnt.items():
			for n2, c2 in f[n1].items():
				ans += "%s\t%s\t%f\n" % (n1, n2, c2 / c1)
		return ans
	
	def corel_str_num(self, a1, a2):
		cnt = {}
		s = {}
		for e in self.data:
			if not a1(e) or not a2(e):
				continue
			if a1(e) not in cnt:
				cnt[a1(e)] = 0
				s[a1(e)] = 0
			cnt[a1(e)] += 1
			s[a1(e)] += a2(e)
		
		ans = ""
		for n, c in cnt.items():
				ans += "%s\t%f\n" % (n, s[n] / c)
		return ans

def nota(e, a):
	if a not in e or e[a] < 1:
		return 0
	return e[a]

def calc_top(crit, top_output, info_output, data):
	materii = {}

	def adauga_nota(s, m, n, r = None):
		if m not in materii:
			materii[m] = {}
		if s not in materii[m]:
			materii[m][s] = {"sum": 0, "cnt": 0, "reusita": 0, "nr_note": 0}

		if r is None:
			r = (n >= 5)

		materii[m][s]["cnt"] += 1
		materii[m][s]["sum"] += n
		materii[m][s]["reusita"] += (1 if r else 0)
		if n > 0:
			materii[m][s]["nr_note"] += 1
	
	info = {}

	def adauga_candidat(t, e, crt, param):
		if param in e:
			if t not in info:
				info[t] = {}
			if crt not in info[t]:
				info[t][crt] = {}
			if e[param] not in info[t][crt]:
				info[t][crt][e[param]] = 0
			info[t][crt][e[param]] += 1

	for e in data:
		t = crit(e)
		adauga_nota(t, "LIMBA ROMANA", nota(e, "lr_final"))
		adauga_nota(t, e["disciplina_obligatorie"], nota(e, "do_final"))
		adauga_nota(t, e["disciplina_la_alegere"], nota(e, "da_final"))
		note = [nota(e, "lr_final"), nota(e, "do_final"), nota(e, "da_final")]
		if "limba_materna" in e:
			adauga_nota(t, e["limba_materna"], nota(e, "lm_final"))
			note.append(nota(e, "lm_final"))
		adauga_nota(t, "GENERAL", sum(note) / len(note) if e["rezultat_final"].upper() in ["REUSIT", "PROMOVAT", "RESPINS"] else 0, e["rezultat_final"].upper() in ["REUSIT", "PROMOVAT"])

		adauga_candidat(t, e, "specializari", "specializare")
		adauga_candidat(t, e, "limba_moderna", "limba_straina")
		aux = e.copy()
		if "limba_materna" not in e:
			aux["limba_romana"] = "LIMBA ROMANA"
			adauga_candidat(t, aux, "limba_materna", "limba_romana")
		else:
			aux["limba_materna"] = aux["limba_materna"].replace(" (UMAN)", "").replace(" (REAL)", "")
			adauga_candidat(t, aux, "limba_materna", "limba_materna")
		adauga_candidat(t, e, "promotie_anterioara", "promotie_anterioara")

	if top_output != None and not os.path.exists(top_output):
		os.mkdir(top_output)
	
	for m, data in materii.items():
		if top_output != None:
			fname = top_output + "/" + unidecode.unidecode(m).upper().replace(" ", "_").replace("/", "-") + ".txt"
			open(fname, "w", encoding="utf-8").write('\n'.join(['%s\t%s\t%.1f\t%d\t%.1f' % (t, "%.2f" % (d["sum"] / d["nr_note"]) if d["nr_note"] > 0 else "-", d["reusita"] / d["cnt"] * 100, d["cnt"], d["cnt"] / materii["GENERAL"][t]["cnt"] * 100) for (t, d) in data.items()]))

		for (t, d) in data.items():
			if t not in info:
				info[t] = {}
			if "materii" not in info[t]:
				info[t]["materii"] = {}
			medie = d["sum"] / d["nr_note"] if d["nr_note"] > 0 else "-"
			info[t]["materii"][m] = {"medie": medie, "reusita": d["reusita"] / d["cnt"] * 100, "cnt": d["cnt"]}
	
	if not os.path.exists(info_output):
		os.mkdir(info_output)
	for t, data in info.items():
		data["nume"] = t
		#print(t)
		fname = info_output + "/" + unidecode.unidecode(t.split('\t')[0]).replace(" ", "_").replace("\"", "_").upper() + ".json"
		#print(fname)
		with open(fname, "w", encoding="utf-8") as f:
			json.dump(data, f)

		

def main(argv):
	if len(argv) < 4 or (len(argv) >= 5 and argv[4] != '--data-dot-gov'):
		print("Usage: python %s dataset_name input_file meta_file [--data-dot-gov]" % (argv[0]))
		return

	if len(argv) >= 5 and argv[4] == '--data-dot-gov':
		global data_dot_gov
		data_dot_gov = True

	bac = Dataset()
	bac.read(argv[2], argv[3])
	
	if not os.path.exists(argv[1]):
		os.mkdir(argv[1])

	calc_top(lambda e : jcode[e["judet"]], argv[1] + "/top_judete", argv[1] + "/info_judete", bac.data)
	calc_top(lambda e : e["liceu"] + '\t' + jcode[e["judet"]], argv[1] + "/top_licee", argv[1] + "/info_licee", bac.data)
	calc_top(lambda e : "România", None, argv[1] + "/info_national", bac.data)

if __name__ == "__main__":
   main(sys.argv)

		
	
