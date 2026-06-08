from simshelpers.util.bot import send_msg, send_file
from simshelpers.markdown import Markdown

md = Markdown("markdown")
md.add_text("Ttile", "h1")
md.add_text("Body Text")
sample_dict = {"Header 1": [1,2,3,4,5], "Header 2": [6,7,8,9,10]}
md.add_divider()
md.add_table(sample_dict)
text = md.save(return_text=True)

send_msg(text)
send_file(r"C:\Users\dylan\sims-helpers\reports\markdown.md")
