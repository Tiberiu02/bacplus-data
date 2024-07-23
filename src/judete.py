import unidecode

judete = [
    ("AB", "ALBA", "Alba"),
    ("AG", "ARGES", "Argeș"),
    ("AR", "ARAD", "Arad"),
    ("B", "BUCURESTI", "București"),
    ("BC", "BACAU", "Bacău"),
    ("BH", "BIHOR", "Bihor"),
    ("BN", "BISTRITA", "Bistrița-Năsăud"),
    ("BR", "BRAILA", "Brăila"),
    ("BT", "BOTOSANI", "Botoșani"),
    ("BV", "BRASOV", "Brașov"),
    ("BZ", "BUZAU", "Buzău"),
    ("CJ", "CLUJ", "Cluj"),
    ("CL", "CALARASI", "Călărași"),
    ("CS", "CARAS", "Caraș-Severin"),
    ("CT", "CONSTANTA", "Constanța"),
    ("CV", "COVASNA", "Covasna"),
    ("DB", "DAMBOVITA", "Dâmbovița"),
    ("DJ", "DOLJ", "Dolj"),
    ("GJ", "GORJ", "Gorj"),
    ("GL", "GALATI", "Galați"),
    ("GR", "GIURGIU", "Giurgiu"),
    ("HD", "HUNEDOARA", "Hunedoara"),
    ("HR", "HARGHITA", "Harghita"),
    ("IF", "ILFOV", "Ilfov"),
    ("IL", "IALOMITA", "Ialomița"),
    ("IS", "IASI", "Iași"),
    ("MH", "MEHEDINTI", "Mehedinți"),
    ("MM", "MARAMURES", "Maramureș"),
    ("MS", "MURES", "Mureș"),
    ("NT", "NEAMT", "Neamț"),
    ("OT", "OLT", "Olt"),
    ("PH", "PRAHOVA", "Prahova"),
    ("SB", "SIBIU", "Sibiu"),
    ("SJ", "SALAJ", "Sălaj"),
    ("SM", "SATU", "Satu Mare"),
    ("SV", "SUCEAVA", "Suceava"),
    ("TL", "TULCEA", "Tulcea"),
    ("TM", "TIMIS", "Timiș"),
    ("TR", "TELEORMAN", "Teleorman"),
    ("VL", "VALCEA", "Vâlcea"),
    ("VN", "VRANCEA", "Vrancea"),
    ("VS", "VASLUI", "Vaslui"),
]

judete_dupa_cod = {
    cod: {"nume": nume, "nume_complet": nume_complet}
    for cod, nume, nume_complet in judete
}


def get_county_code(county_name):
    name = unidecode.unidecode(county_name).upper()

    for code, county, county_name in judete:
        if county in name:
            return code

    raise Exception(f"Unknown county {name}")
