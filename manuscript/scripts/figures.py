"""Render the five vector figures from the extraction CSVs."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def records(name):
    with (ROOT/"data"/(name+".csv")).open() as f:
        return list(csv.DictReader(f))
C="#125c70"; A="#a04e23"; INK="#202b31"; GREY="#69767c"
plt.rcParams.update({"font.size":9,"axes.labelcolor":INK,"text.color":INK,"axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42,"axes.titlelocation":"left","axes.titleweight":"bold","axes.titlesize":10})
def finish(fig,n):
    fig.savefig(ROOT/"figures"/f"fig{n}.pdf",bbox_inches="tight",pad_inches=.08)
    plt.close(fig)

def worked():
    fig,(ax,bx)=plt.subplots(1,2,figsize=(6.55,2.20),layout="constrained",width_ratios=[1,1.12])
    ax.set_title("A   Data-generating graph")
    nodes={"Population":(.21,.86),"Stratum S":(.73,.86),"Risk U":(.48,.53),"Regime M":(.18,.19),"Action A":(.50,.19),"Success Y":(.84,.52)}
    boxes={}
    for name,(x,y) in nodes.items():
        label=ax.text(x,y,name,ha="center",va="center",fontsize=8,bbox=dict(boxstyle="round,pad=.28",facecolor="white",edgecolor="#afbec3"))
        boxes[name]=label.get_bbox_patch()
    ax.set(xlim=(0,1.03),ylim=(-.07,1.07));ax.axis("off")
    for left,right,dash in [("Population","Stratum S",0),("Stratum S","Success Y",0),("Risk U","Success Y",0),("Risk U","Action A",1),("Regime M","Action A",0),("Action A","Success Y",0)]:
        ax.annotate("",xy=nodes[right],xytext=nodes[left],arrowprops=dict(arrowstyle="-|>",lw=1.25,color=GREY,patchA=boxes[left],patchB=boxes[right],shrinkA=1,shrinkB=1,linestyle="--" if dash else "-"))
    bx.set_title("B   Family 096: target effects")
    q=records("quartets")[96]
    weights=[int(q["w0"]),int(q["w1"])]
    for j,(name,color,mark) in enumerate([("L randomized",C,"o"),("R randomized",A,"s")]):
        y=[float(q[f"d{j}{k}"]) for k in range(2)]
        bx.plot(weights,y,marker=mark,color=color,label=name,lw=1.8)
        for x,v in zip(weights,y):
            bx.annotate(f"{v:+.3f}".rstrip("0"),(x,v),xytext=(0,7 if v>0 else -11),textcoords="offset points",ha="center",fontsize=8)
    bx.axhline(0,lw=.7,c=GREY); bx.set(xlim=(52,89),ylim=(-1.9,2.1),xticks=[58,83],xlabel="Target share of first stratum (%)",ylabel="On minus off (pp)")
    bx.legend(loc="lower center",bbox_to_anchor=(.50,-.54),ncol=2,frameon=False,fontsize=8)
    finish(fig,1)

def design():
    data=records("quartets")
    fig,axes=plt.subplots(1,4,figsize=(6.6,1.82),layout="constrained")
    for ax,(p,g) in zip(axes,[(0,0),(0,1),(1,0),(1,1)]):
        group=[r for r in data if int(r["p"])==p and int(r["g"])==g]
        first=next(r for r in group if int(r["b"])==1)
        for role in (0,1):
            actions = tuple(int(float(first[f"d{role}{k}"]) > 0) for k in (0, 1))
            for k,v in enumerate(actions):
                ax.add_patch(FancyBboxPatch((k-.43,role-.38),.86,.76,boxstyle="round,pad=.02,rounding_size=.08",facecolor=C if v else "#e7edef",edgecolor="none"))
                ax.text(k,role,str(int(v)),color="white" if v else INK,ha="center",va="center",fontsize=12)
            ax.text(2.2, role, str(int(actions == (1, 0))), color=INK, ha="center", va="center", fontsize=12)
        ax.axvline(1.64, ymin=.09, ymax=.91, color="#afbec3", lw=.8)
        ax.text(1.0,-.54,"1 = On, 0 = Off",ha="center",va="bottom",transform=ax.transAxes,fontsize=7,color=GREY)
        ax.set(xticks=[0,1,2.2],xticklabels=["Mix 0","Mix 1","Credit"],yticks=[0,1],yticklabels=["L","R"],xlim=(-.55,2.68),ylim=(1.55,-.55))
        ax.tick_params(axis="x",labelsize=8)
        ax.set_title(["Both stable","Role switches","Mix switches","Both switch"][p*2+g],fontsize=9)
        ax.tick_params(length=0); ax.spines[:].set_visible(False)
    finish(fig,2)

def primary():
    dat=records("intervals")
    fig,(ax,bx)=plt.subplots(1,2,figsize=(6.5,1.8),layout="constrained")
    for axis,subset,names,colors,title in [(ax,dat[:2],["Causal","Arithmetic"],[C,A],"A   Target-pair fidelity"),(bx,dat[2:],["Approx. t","Bounded"],[INK,GREY],"B   Paired difference")]:
        for y,(r,color) in enumerate(zip(subset,colors)):
            m,l,h=[100*float(r[k]) for k in ("mean","low","high")]
            axis.errorbar(m,y,xerr=[[m-l],[h-m]],fmt="o",color=color,capsize=4,ms=5)
        axis.set(yticks=[0,1],yticklabels=names,ylim=(1.7,-.7));axis.set_title(title);axis.grid(axis="x",alpha=.18)
    ax.set(xlim=(0,40),xlabel="Both correct (%)")
    bx.axvline(0,ls="--",lw=.8,c=GREY);bx.set(xlim=(-32,27),xlabel="Causal minus arithmetic (pp)")
    finish(fig,3)

def transitions():
    dat=[r for r in records("pairs") if r["form"]=="1" and r["axis"]=="target"]
    fig,(ax,bx)=plt.subplots(1,2,figsize=(6.55,1.9),layout="constrained",sharex=True)
    for a,s,title in [(ax,1,"A   Reversal required"),(bx,0,"B   Invariance required")]:
        rows=sorted([r for r in dat if int(r["switch"])==s],key=lambda r:r["task"])
        for j,r in enumerate(rows):
            left=0
            for key,color in [("both",C),("one","#a9bac1"),("neither","#e8dddd")]:
                v=int(r[key]);a.barh(j,v,left=left,color=color,height=.53,edgecolor="white",linewidth=.7)
                if v>=15:a.text(left+v/2,j,str(v),ha="center",va="center",color="white" if key=="both" else INK,fontsize=8)
                left+=v
            if s==1 and r["task"]=="0":
                a.annotate("3 both correct",xy=(3,j),xytext=(35,j-.38),textcoords="data",fontsize=7,color=C,arrowprops=dict(arrowstyle="-",color=C,lw=.6))
                a.annotate("5 both wrong",xy=(253,j),xytext=(155,j-.38),textcoords="data",fontsize=7,color=INK,arrowprops=dict(arrowstyle="-",color=INK,lw=.6))
        a.set(yticks=[0,1],yticklabels=["Causal","Arithmetic"],ylim=(1.6,-.6),xlim=(0,256),xticks=[0,64,128,192,256],xlabel="Scheduled target pairs");a.set_title(title)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=c,label=l) for c,l in [(C,"Both correct"),("#a9bac1","One correct"),("#e8dddd","Both wrong")]],loc="lower center",bbox_to_anchor=(.5,-.17),ncol=3,frameon=False,fontsize=8)
    finish(fig,4)

def order():
    data=[r for r in records("order016") if r["conflict"]=="1"]
    fig,(ax,bx)=plt.subplots(1,2,figsize=(6.55,2.15),layout="constrained")
    for arm,col,mark in [("Q4_K_M",C,"o"),("F16",A,"s")]:
        yy=[]
        for o in ["randomized_first","historical_first"]:
            group=[r for r in data if r["order"]==o and r["arm"]==arm]
            yy.append(100*sum(r["gold"]==r["action"] for r in group)/len(group))
        ax.plot([0,1],yy,marker=mark,color=col,label=arm)
    ax.set_title("A   Conflict decisions");ax.set(ylabel="Correct (%)",ylim=(0,105),xlim=(-.18,1.18),xticks=[0,1],xticklabels=["Trial first","History first"])
    ax.legend(frameon=False,fontsize=8); ax.grid(axis="y",alpha=.18)
    unique={r["family"]:r for r in data if r["arm"]=="F16" and r["order"]=="randomized_first"}
    bx.scatter([float(r["random_gap"]) for r in unique.values()],[float(r["historical_gap"]) for r in unique.values()],s=10,alpha=.64,c=C)
    bx.plot([0,45],[0,45],ls="--",color=GREY,lw=.8)
    bx.set_title("B   Source-blind separation");bx.set(xlabel="Absolute trial gap (pp)",ylabel="Absolute history gap (pp)",xlim=(0,45),ylim=(0,50))
    finish(fig,5)

if __name__=="__main__":
    worked()
    design()
    primary()
    transitions()
    order()
