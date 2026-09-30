"""
Test script for MatchmakerOrchestrator fleet execution.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules['torchvision'] = None

from agent.orchestrator import MatchmakerOrchestrator
import time

def run_test():
    print("Initializing Orchestrator...")
    orchestrator = MatchmakerOrchestrator()
    start_time = time.time()
    
    # Run fleet matching
    results = orchestrator.run_matchmaking_fleet()
    elapsed = round(time.time() - start_time, 2)
    
    print("\n================ FLEET MATCH RESULTS ================")
    print(f"Total Patients: {results['total_patients']}")
    print(f"Total Active Trials: {results['total_trials']}")
    print(f"Total Evaluated Pairs: {results['total_evaluated_pairs']}")
    print(f"High-Confidence Matches: {results['high_match_count']}")
    print(f"Needs Verification: {results['verification_needed_count']}")
    print(f"Excluded / Not Suitable: {results['excluded_count']}")
    print(f"Execution Time: {elapsed} seconds")
    
    # Inspect Trial T01 candidate ranking
    t01_matches = results['by_trial'].get('T01', [])
    print(f"\nTop Candidates for Trial T01 (DIAMOND-MET): {len(t01_matches)} total")
    for cand in t01_matches[:3]:
        print(f" - {cand['patient_id']} ({cand['patient_name']}): Score {cand['match_score']}% [{cand['tier']}]")
        print(f"   Summary: {cand['summary']}")
        if cand['action_items']:
            print(f"   Action items: {cand['action_items']}")
            
    # Inspect Patient P001 trial opportunities
    p001_matches = results['by_patient'].get('P001', [])
    print(f"\nTrial Opportunities for Patient P001: {len(p001_matches)} total")
    for t in p001_matches[:3]:
        print(f" - {t['trial_id']} ({t['trial_name']}): Score {t['match_score']}% [{t['tier']}]")
        
    print("\n>>> MATCHMAKER ORCHESTRATOR TEST COMPLETED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    run_test()
