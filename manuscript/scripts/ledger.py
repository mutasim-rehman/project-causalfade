"""Make the study history and claim ledger from tagged Git objects."""
import csv
import hashlib
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parents[1]
TAG="76206c259caa488668a7556ce1bc53cb35d220da"
HISTORY=[
("001","Pilot","Direct causal decisions from exact counts. The low-precision arm exhausted its token budget. A format-sensitive endpoint limited the proposed compression comparison.","f16_vs_q2_k.json"),
("002","Control","Giving the arithmetic formula separated the sign of a numerical estimate from the explicitly selected action. Single-fence handling mattered to the result.","estimate_sign_policy_sensitivity.json"),
("003","Technical diagnostic","Disabling CPU repacking did not rescue Q2 output. Repeated items checked operational reproducibility and added no independent families.","response_agreement.json"),
("004","Reference screen","The larger F16 reference missed the competence gate on direct prompts. That gate constrained interpretation of a weaker format.","reference_feasibility.json"),
("005","Development","Supplying randomized and historical rates made source selection explicit. Action preference and tree-model misfit complicated the conflict-penalty interpretation.","source_and_tree_diagnostics.json"),
("006","Control follow-up","Q8 reproduced the strong F16 sign performance on the reused formula tasks. Signs and actions remained separate endpoints.","run_001_f16_vs_q8_0_estimate_sign.json"),
("007","Fresh-family replication","The sign result recurred under the supplied formula. On the same 48 items, F16/Q4 sign scores were 46/31 correct and overt action scores were 24/28 correct. All replies were fenced.","paired_estimate_sign.json paired_explicit_action.json"),
("008","Development crossover","An interrupted F16 run was retained. Completed order arms, rather than partial-run scores with unattempted items, supplied the order comparison.","source_order_analysis.json"),
("009","Development crossover","Interleaving both evidence orders reduced the between-run confound. An early summary halved success and activation counts. Corrected counts preserve paired effects.","source_order_analysis.json"),
("010","Fresh-family follow-up","The 3B order pattern recurred on new numerical families. The family-bootstrap analysis followed earlier observations. The original count underreporting was corrected.","source_order_analysis.json"),
("011","Development","Historical strength was matched across agreement conditions. The quantized model's action preference could reduce an apparent conflict penalty. Corrected count output is used.","format_analysis.json source_order_analysis.json"),
("012","Reference screen","The matched-strength 7B F16 reference failed conflict-specific competence in both evidence orders under the fence-tolerant score.","gate_analysis.json"),
("013","Development crossover","The causal-context frame produced capped continuations. A later prefix diagnostic exposed a parseable opening answer but did not rescue the frozen endpoint.","analysis.json"),
("014","Development crossover","A stricter response instruction restored valid outputs. Neither reference framing cleared all performance gates.","analysis.json"),
("015","Reference screen","The fresh-family F16 gate passed, enabling a conditional Q4 arm. Its observed conflict-order pattern motivated a separate prospective hypothesis.","gate_analysis.json order_analysis.json"),
("016","Prospective confirmation","A frozen 96-family design confirmed the Q4 conflict-order contrast. Precision interactions were secondary. The magnitude counterexample is retrospective.","frozen_run_plan.json primary_analysis.json"),
("017","Exploratory extension","Larger 14B quantized arms reused the 016 fixture. The large 7B conflict-order effect did not recur. Archived responses supported post-run analysis recovery.","analysis.json analysis_recovery.json"),
("018","Development gate","Matched controls and graded evidence were introduced. F16 failed the decision gate, so no Q4 comparison followed.","development_analysis.json"),
("019","Development gate","Semantic and reversed neutral response contracts changed the mapping to an action. Conflicting prose about which source came first weakened a comprehension probe. The official gate failed.","development_analysis.json"),
("020","Component screen","Single-number and randomized-only components were comparatively tractable. Adding a second source exposed interference and order dependence.","development_analysis.json"),
("021","Guidance screen","All 128 governing-source selections were correct. Ordinary and explicitly guided two-source decisions each scored 58/128. Naming evidence and acting on it are distinct outputs.","development_analysis.json"),
("022","Development replication","A fresh matched fixture compared Qwen and Mistral deployments. Failure on simpler Mistral components limited cross-checkpoint attribution.","development_analysis.json"),
("023","Measurement audit","Crossing source names, physical display and option position left a two-source deficit. Weak harmful-direction numeric and noncausal controls precluded specificity.","development_analysis.json development_supplement.json"),
("024","Development matrix","Three lineages and seven formats completed the matrix. Output caps and first-option policies affected particular arms. No F16 passed all of the later component/control diagnostics.","frozen_lab_plan.json development_analysis_archive.json"),
("025","Retrospective","Archived responses were reanalyzed for matched transitions, information dependence and metamorphic behavior. Reused observations cannot confirm an independently selected hypothesis.","archive_methods_screen.json"),
("025.1","Retrospective audit","An applicability audit reproduced the archive screen and distinguished methods the existing data could support from methods requiring new graded evidence or interventions.","archive_investigation.json"),
("026","Development gate","Observationally identical confounder/mediator graphs required different decisions. A faulty complemented-outcome arithmetic key invalidated the first pilot. Repaired forms failed qualification.","frozen_development_plan.json development_summary.md"),
("027","Development gate","Fully crossing answer order addressed a position confound. No tested development arm qualified. Higher-memory models and later validation/precision arms contributed no outcome data.","plan.json pipeline_status.json"),
("028","Development gate","Bare, structured and calculator-assisted procedures separated computation from procedure choice. Development finished and the gate stopped the pipeline. The earlier pause in the README is stale.","plan.json pipeline_status.json"),
("029","Prospective case study","CF-TP1 crossed feasible provenance, target mix, order, form and matched arithmetic. The primary contrast was inconclusive. No new precision arm was part of this protocol.","freeze/protocol.md runs/confirmatory/analysis/primary.json")]
def tex(s):
    return s.replace("&",r"\&").replace("%",r"\%").replace("_",r"\_")

def main():
    led=[]
    entries=[]
    def claim(section,claim,paths,method):
        for path in paths.split():
            data=subprocess.check_output(["git","show",TAG+":"+path],cwd=HERE.parent)
            led.append([section,claim,method,path,hashlib.sha256(data).hexdigest(),TAG])
    for number,status,summary,paths in HISTORY:
        folder="experiments/cohort_"+number.replace(".","_")+"/"
        claim("History "+number,summary," ".join(folder+p for p in paths.split()),status)
        entries.append(tex(number)+" & "+tex(status)+" & "+tex(summary)+r" \\[3pt]")
    (HERE/"history.tex").write_text("\n".join(entries)+"\n",encoding="utf8")
    root="experiments/cohort_029/"
    def c(section,finding,paths,method):
        claim(section,finding," ".join(root+p for p in paths.split()),method)
    c("Introduction and methods / Fig 1","SCM, alternative assignment feasibility, exact family 096 and positive margins","freeze/protocol.md freeze/fixture/worlds.jsonl freeze/fixture/gold.jsonl freeze/fixture/public_oracle.jsonl","Exact arithmetic; extract.py and example/quartets CSV")
    c("Introduction and methods / Fig 2 / Table 1","128 slots, eight sign strata, complete crossing; public form/order and prompt hashes","freeze/manifest.json freeze/fixture/design.jsonl freeze/fixture/tasks.jsonl freeze/fixture/schedule.json freeze/fixture/structural_diffs.json freeze/fixture/fixture_audit.json","Release verifier and quartets.csv; figure credit compares both oracle actions with the illustrative (1,0) sequence")
    c("Setup","Token lengths, hardware flags, checkpoint and server provenance","freeze/deployment/inventory.json freeze/deployment/token_budget.json","Frozen configuration and per-task counts")
    c("Primary / Fig 3","128 and 146 both-correct pairs out of 512; family D, SE, df, t and bounded intervals","runs/confirmatory/events.jsonl runs/confirmatory/analysis/primary.json runs/confirmatory/analysis/family_scores.jsonl freeze/evidence/coverage.json","Raw journal and independently aggregated intervals.csv; arm intervals are descriptive")
    c("Table 2 / Fig 4","Switch, invariant, role and order counts; zeros, ones and twos; archive contrast","runs/confirmatory/analysis/pair_scores.jsonl runs/confirmatory/analysis/secondary.json runs/confirmatory/events.jsonl","Joined by six indices and tested against released pair cells; pairs.csv")
    c("Table 2 / direction reconciliation","Correct off/on: causal 14/497, arithmetic 231/316, each gold denominator 512. Activation 995 and 597 /1024.","runs/confirmatory/events.jsonl freeze/fixture/gold.jsonl runs/confirmatory/analysis/row_scores.jsonl runs/confirmatory/analysis/secondary.json release/RESULTS.md","Raw response_b64 by ID; compare with row_cells. Narrative direction table is superseded for these claims.")
    c("Response validity / position","No missing or invalid answers; answer-order accuracy and activation by displayed first option","runs/confirmatory/terminal.json runs/confirmatory/events.jsonl freeze/fixture/public_oracle.jsonl","Strict payload and stop check; public options[0]; direction.csv and option_order.csv")
    c("Table 3 / policies","Both tie conventions; 12 literal failures, clarified pass. All item and paired numerators, constant and positive controls","freeze/fixture/policy_audit.json freeze/policy-clarification.md","policies.csv; per-policy item predictions in two frozen gzip files")
    c("Provenance / timing","Original journal and freeze; postcollection analysis; human independence undocumented at freeze","release/PROVENANCE_AND_LIMITATIONS.md release/validation_record.json freeze/evidence/provenance.json","Signed later evidence described separately; attribution and licensing limited")
    c("Reproduction","Release verifier, replay and archived checks","release/verification.json runs/confirmatory/reproduction/reproduction_report.json release/REPRODUCE.md","See audit/ for manuscript-side rerun")
    p16="experiments/cohort_016/"
    claim("016 / Fig 5","Conflict and aligned accuracy by format, family t and bootstrap intervals; smaller absolute printed contrast solves 768/768"," ".join(p16+s for s in ["input/public_tasks.jsonl","input/oracle_truth.jsonl","run_001_7b_f16/raw_responses.jsonl","run_002_7b_q4_k_m/raw_responses.jsonl","primary_analysis.json","frozen_run_plan.json"]),"order016.csv and retrospective source-blind parser; semi-independent corroboration of archived statistics")
    claim("Availability","MIT software / scoped CC BY 4.0 numerical data; transfer wording excluded","LICENSES.md","Tagged rights statement")
    with (HERE/"audit/claim-ledger.csv").open("w",newline="",encoding="utf8") as f:
        w=csv.writer(f);w.writerow(["location","claim","classification_or_check","tagged_path","sha256_git_blob_content","release_commit"]);w.writerows(led)
if __name__=="__main__":
    main()
