from pathlib import Path
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]
out=root/'analysis/output'
out.mkdir(exist_ok=True)
with sqlite3.connect((root/'data/payroll.db').as_uri()+'?mode=ro',uri=True) as db:
    queries=[
        ('absence','Recorded absence by month','Absent days','SELECT month,sum(absent) FROM summary GROUP BY month ORDER BY month'),
        ('attendance','Presence by department','Percent of recorded days','SELECT department,100.0*sum(present)/NULLIF(sum(recorded),0) FROM summary GROUP BY department'),
        ('salary','Monthly net payroll','INR','SELECT month,sum(net_paise)/100.0 FROM payroll GROUP BY month ORDER BY month')]
    for file,title,unit,query in queries:
        rows=[(label,float(value)) for label,value in db.execute(query) if value is not None]
        fig,ax=plt.subplots(figsize=(7,4))
        bars=ax.bar([r[0] for r in rows],[r[1] for r in rows],color='#206878',width=.55)
        ax.bar_label(bars,fmt='%.1f',padding=4)
        ax.set(title=title,ylabel=unit);ax.margins(y=.2)
        fig.tight_layout();fig.savefig(out/(file+'.png'),dpi=140);plt.close(fig)
        print(title,rows)
