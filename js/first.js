
let btn = document.getElementById('ContentPlaceHolderBody_ImageButtonST2')

if (!btn)
  btn = [... document.querySelectorAll('a')].filter(el => el.textContent == '<<')[0]

if (btn)
  btn.click()