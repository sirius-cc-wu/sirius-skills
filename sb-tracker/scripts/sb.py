#!/usr/bin/env python3
"""
Simple Beads (sb) - A minimal, standalone issue tracker for individuals.
No git hooks, no complex dependencies, just one JSON file.
"""

import json
import os
import sys
from datetime import datetime

def find_db_path():
    """Walk up the directory tree to find .sb.json."""
    cwd = os.getcwd()
    while cwd != os.path.dirname(cwd):  # Stop at root
        potential_path = os.path.join(cwd, ".sb.json")
        if os.path.exists(potential_path):
            return potential_path
        # Also stop at git root to keep it project-local
        if os.path.exists(os.path.join(cwd, ".git")):
            return os.path.join(cwd, ".sb.json")
        cwd = os.path.dirname(cwd)
    return os.path.join(os.getcwd(), ".sb.json")

DB_FILE = find_db_path()

def load_db():
    if not os.path.exists(DB_FILE):
        return {"issues": []}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"issues": []}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def init():
    if os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} already exists.")
        return
    save_db({"issues": []})
    print(f"Initialized Simple Beads in {DB_FILE}")

def search_issues(keyword, as_json=False):
    db = load_db()
    keyword = keyword.lower()
    results = []
    for i in db["issues"]:
        if keyword in i["title"].lower() or keyword in i.get("description", "").lower():
            results.append(i)
    
    if as_json:
        print(json.dumps(results, indent=2))
        return
    
    if not results:
        print(f"No results found for '{keyword}'")
        return
        
    print(f"Search results for '{keyword}':")
    print(f"{'ID':<12} {'Status':<12} {'Title'}")
    print("-" * 60)
    for i in results:
        print(f"{i['id']:<12} {i['status']:<12} {i['title']}")

def update_issue(issue_id, title=None, description=None, priority=None, parent_id=None):
    db = load_db()
    issue = next((i for i in db["issues"] if i["id"] == issue_id), None)
    if not issue:
        print(f"Error: Issue {issue_id} not found.")
        return

    changes = {}
    if title:
        changes["title"] = (issue["title"], title)
        issue["title"] = title
    if description is not None:
        changes["description"] = "updated"
        issue["description"] = description
    if priority is not None:
        changes["priority"] = (issue.get("priority", 2), priority)
        issue["priority"] = priority
    if parent_id is not None:
        # Hierarchy change
        old_parent = issue.get("parent")
        if parent_id == "": # Remove parent
            if "parent" in issue: del issue["parent"]
            changes["parent"] = (old_parent, None)
        else:
            issue["parent"] = parent_id
            changes["parent"] = (old_parent, parent_id)

    if changes:
        log_event(issue, "updated", {"changes": changes})
        save_db(db)
        print(f"Updated {issue_id}")
    else:
        print("No changes specified.")

def promote_issue(issue_id):
    db = load_db()
    issue = next((i for i in db["issues"] if i["id"] == issue_id), None)
    if not issue:
        print(f"Error: Issue {issue_id} not found.")
        return

    children = [i for i in db["issues"] if i.get("parent") == issue_id]
    
    print(f"### [{issue['id']}] {issue['title']}")
    print(f"**Status:** {issue['status']} | **Priority:** P{issue.get('priority', 2)}")
    if issue.get("description"):
        print(f"\n{issue['description']}")
    
    if children:
        print("\n#### Sub-tasks")
        for child in children:
            check = "x" if child["status"] == "closed" else " "
            print(f"- [{check}] {child['id']}: {child['title']}")
    
    if issue.get("events"):
        print("\n#### Activity Log")
        for e in issue["events"]:
            ts = e["timestamp"].split("T")[0]
            if e["type"] == "created":
                print(f"- {ts}: Created")
            elif e["type"] == "status_changed":
                print(f"- {ts}: {e['old']} -> {e['new']}")
            elif e["type"] == "updated":
                print(f"- {ts}: Details updated")

def log_event(issue, event_type, details=None):
    event = {
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
    }
    if details:
        event.update(details)
    if "events" not in issue:
        issue["events"] = []
    issue["events"].append(event)

def add(title, description="", priority=2, depends_on=None, parent_id=None):
    db = load_db()
    
    if parent_id:
        parent = next((i for i in db["issues"] if i["id"] == parent_id), None)
        if not parent:
            print(f"Error: Parent issue {parent_id} not found.")
            return
        
        prefix = parent_id + "."
        children = [i for i in db["issues"] if i["id"].startswith(prefix)]
        max_sub = 0
        for child in children:
            sub_part = child["id"][len(prefix):]
            if "." not in sub_part:
                try:
                    val = int(sub_part)
                    if val > max_sub:
                        max_sub = val
                except ValueError: continue
        new_id = f"{prefix}{max_sub + 1}"
    else:
        max_id = 0
        for issue in db["issues"]:
            if "." not in issue["id"]:
                try:
                    if "-" in issue["id"]:
                        val = int(issue["id"].split("-")[1])
                        if val > max_id: max_id = val
                except (IndexError, ValueError): continue
        new_id = f"sb-{max_id + 1}"

    issue = {
        "id": new_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "open",
        "depends_on": depends_on or [],
        "events": [],
        "created_at": datetime.now().isoformat()
    }
    if parent_id:
        issue["parent"] = parent_id
        
    log_event(issue, "created", {"title": title})
    db["issues"].append(issue)
    save_db(db)
    print(f"Created {new_id}: {title} (P{priority})")

def add_dependency(child_id, parent_id):
    db = load_db()
    child = next((i for i in db["issues"] if i["id"] == child_id), None)
    parent = next((i for i in db["issues"] if i["id"] == parent_id), None)
    
    if not child:
        print(f"Error: Child issue {child_id} not found.")
        return
    if not parent:
        print(f"Error: Parent issue {parent_id} not found.")
        return
        
    if parent_id not in child["depends_on"]:
        child["depends_on"].append(parent_id)
        log_event(child, "dep_added", {"parent": parent_id})
        save_db(db)
        print(f"Linked {child_id} -> depends on -> {parent_id}")
    else:
        print(f"Already linked.")

def is_ready(issue, all_issues):
    if issue["status"] != "open":
        return False
    
    # Check if all dependencies are closed
    for dep_id in issue.get("depends_on", []):
        dep = next((i for i in all_issues if i["id"] == dep_id), None)
        if dep and dep["status"] != "closed":
            return False
    return True

def list_issues(show_all=False, as_json=False, ready_only=False):
    db = load_db()
    all_issues = db["issues"]
    
    if ready_only:
        issues = [i for i in all_issues if is_ready(i, all_issues)]
    elif not show_all:
        issues = [i for i in all_issues if i["status"] == "open"]
    else:
        issues = all_issues
    
    # Sort by ID (to keep hierarchy together), then priority
    issues.sort(key=lambda x: (x["id"], x.get("priority", 2)))

    if as_json:
        # Include compaction log in JSON if it exists
        output = {"issues": issues}
        if db.get("compaction_log"):
            output["compaction_log"] = db["compaction_log"]
        print(json.dumps(output, indent=2))
        return

    if not issues:
        print("No issues found matching criteria.")
        if db.get("compaction_log"):
            print("\nCompaction Log (Archived):")
            for entry in db["compaction_log"]:
                print(f"  - {entry['summary']}")
        return

    print(f"{'ID':<12} {'P':<2} {'Status':<12} {'Deps':<10} {'Title'}")
    print("-" * 80)
    for i in issues:
        status = i["status"]
        deps = ",".join(i.get("depends_on", []))
        if len(deps) > 10: deps = deps[:7] + "..."
        # Indent children
        indent = "  " * i["id"].count(".")
        print(f"{i['id']:<12} {i.get('priority', 2):<2} {status:<12} {deps:<10} {indent}{i['title']}")

def show_stats():
    db = load_db()
    issues = db["issues"]
    
    total = len(issues)
    open_count = len([i for i in issues if i["status"] == "open"])
    closed_count = len([i for i in issues if i["status"] == "closed"])
    ready_count = len([i for i in issues if is_ready(i, issues)])
    
    p_counts = {}
    for i in issues:
        p = f"P{i.get('priority', 2)}"
        p_counts[p] = p_counts.get(p, 0) + 1

    print("════════════════════════════════════════")
    print("  SB Tracker Statistics")
    print("════════════════════════════════════════")
    print(f"Total Issues:   {total}")
    print(f"Open:           {open_count}")
    print(f"Ready:          {ready_count}")
    print(f"Closed:         {closed_count}")
    print("----------------------------------------")
    print("Priority Breakdown:")
    for p in sorted(p_counts.keys()):
        print(f"  {p}: {p_counts[p]}")
    
    if db.get("compaction_log"):
        print("----------------------------------------")
        print(f"Archived via Compaction: {len(db['compaction_log'])} entries")
    print("════════════════════════════════════════")

def compact():
    db = load_db()
    closed_issues = [i for i in db["issues"] if i["status"] == "closed"]
    
    if not closed_issues:
        print("No closed issues to compact.")
        return

    summary_parts = []
    for i in closed_issues:
        summary_parts.append(f"{i['id']}: {i['title']}")
    
    summary_text = f"Compacted {len(closed_issues)} issues on {datetime.now().strftime('%Y-%m-%d %H:%M')}: " + ", ".join(summary_parts)
    
    if "compaction_log" not in db:
        db["compaction_log"] = []
    
    db["compaction_log"].append({
        "timestamp": datetime.now().isoformat(),
        "count": len(closed_issues),
        "summary": summary_text
    })
    
    # Remove closed issues
    db["issues"] = [i for i in db["issues"] if i["status"] != "closed"]
    
    save_db(db)
    print(f"Successfully compacted {len(closed_issues)} issues.")
    print(f"Archive entry added to compaction_log.")

def update_status(issue_id, status):
    db = load_db()
    for i in db["issues"]:
        if i["id"] == issue_id:
            old_status = i["status"]
            if old_status == status: return
            i["status"] = status
            log_event(i, "status_changed", {"old": old_status, "new": status})
            if status == "closed":
                i["closed_at"] = datetime.now().isoformat()
            save_db(db)
            print(f"Updated {issue_id} status to {status}")
            return
    print(f"Error: Issue {issue_id} not found.")

def delete_issue(issue_id):
    db = load_db()
    original_count = len(db["issues"])
    db["issues"] = [i for i in db["issues"] if i["id"] != issue_id]
    if len(db["issues"]) < original_count:
        save_db(db)
        print(f"Deleted {issue_id}")
    else:
        print(f"Error: Issue {issue_id} not found.")

def show_issue(issue_id, as_json=False):
    db = load_db()
    for i in db["issues"]:
        if i["id"] == issue_id:
            if as_json:
                print(json.dumps(i, indent=2))
            else:
                print(f"ID:          {i['id']}")
                print(f"Title:       {i['title']}")
                print(f"Priority:    P{i.get('priority', 2)}")
                print(f"Status:      {i['status']}")
                print(f"Created:     {i['created_at']}")
                print(f"Depends On:  {', '.join(i.get('depends_on', [])) or 'None'}")
                
                dependents = [dep['id'] for dep in db["issues"] if i['id'] in dep.get('depends_on', [])]
                print(f"Blocking:    {', '.join(dependents) or 'None'}")
                
                if i.get("description"):
                    print(f"\nDescription:\n{i['description']}")
                
                if i.get("events"):
                    print("\nAudit Log:")
                    for e in i["events"]:
                        ts = e["timestamp"].split("T")[1][:8]
                        if e["type"] == "created":
                            print(f"  [{ts}] Created")
                        elif e["type"] == "status_changed":
                            print(f"  [{ts}] Status: {e['old']} -> {e['new']}")
                        elif e["type"] == "dep_added":
                            print(f"  [{ts}] Dependency added: {e['parent']}")
            return
    print(f"Error: Issue {issue_id} not found.")

def main():
    if len(sys.argv) < 2:
        print("Usage: sb <command> [args]")
        print("Commands:")
        print("  init                      Initialize .sb.json")
        print("  add <title> [p] [desc] [parent]   Add issue")
        print("  list [--all] [--json]     List issues")
        print("  ready [--json]            List issues with no open blockers")
        print("  search <keyword> [--json] Search titles and descriptions")
        print("  stats                     Show task statistics")
        print("  compact                   Archive closed issues")
        print("  dep <child> <parent>      Add dependency")
        print("  update <id> [field=val]   Update title, desc, p, parent")
        print("  promote <id>              Export task as Markdown")
        print("  show <id> [--json]        Show issue details")
        print("  done <id>                 Close issue")
        print("  rm <id>                   Delete issue")
        return

    cmd = sys.argv[1]
    if cmd == "init":
        init()
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: sb add <title> [priority] [description] [parent_id]")
        else:
            title = sys.argv[2]
            p = 2
            desc = ""
            parent = None
            
            args = sys.argv[3:]
            if args:
                try:
                    p = int(args[0])
                    args = args[1:]
                except ValueError: pass
            
            if args:
                desc = args[0]
                args = args[1:]
            
            if args:
                parent = args[0]
                
            add(title, desc, p, parent_id=parent)
    elif cmd == "list":
        show_all = "--all" in sys.argv
        as_json = "--json" in sys.argv
        list_issues(show_all, as_json)
    elif cmd == "ready":
        as_json = "--json" in sys.argv
        list_issues(as_json=as_json, ready_only=True)
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: sb search <keyword> [--json]")
        else:
            as_json = "--json" in sys.argv
            search_issues(sys.argv[2], as_json)
    elif cmd == "update":
        if len(sys.argv) < 3:
            print("Usage: sb update <id> [title=...] [desc=...] [p=...] [parent=...]")
        else:
            issue_id = sys.argv[2]
            kwargs = {}
            for arg in sys.argv[3:]:
                if "=" in arg:
                    k, v = arg.split("=", 1)
                    if k == "p": kwargs["priority"] = int(v)
                    elif k == "title": kwargs["title"] = v
                    elif k == "desc": kwargs["description"] = v
                    elif k == "parent": kwargs["parent_id"] = v
            update_issue(issue_id, **kwargs)
    elif cmd == "promote":
        if len(sys.argv) < 3:
            print("Usage: sb promote <id>")
        else:
            promote_issue(sys.argv[2])
    elif cmd == "stats":
        show_stats()
    elif cmd == "compact":
        compact()
    elif cmd == "dep":
        if len(sys.argv) < 4:
            print("Usage: sb dep <child_id> <parent_id>")
        else:
            add_dependency(sys.argv[2], sys.argv[3])
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("Usage: sb show <id> [--json]")
        else:
            as_json = "--json" in sys.argv
            show_issue(sys.argv[2], as_json)
    elif cmd == "done":
        if len(sys.argv) < 3:
            print("Usage: sb done <id>")
        else:
            update_status(sys.argv[2], "closed")
    elif cmd == "rm":
        if len(sys.argv) < 3:
            print("Usage: sb rm <id>")
        else:
            delete_issue(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
