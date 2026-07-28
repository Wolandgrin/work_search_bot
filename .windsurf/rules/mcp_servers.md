---
trigger: always_on
description:
globs:
---

# MCP Tools — Quick Reference

Credentials: `.env.mcps`. Config: `mcp_config.json` → sync to `~/.codeium/windsurf/mcp_config.json`.

## Jenkins CLI
```bash
python3 ~/Documents/code/MCPs/jenkins_cli.py list|folder|search|job|build|log|stop
```
URL: https://ati-aqa-jenkins.do.acronis.fun

## TestRail CLI
```bash
python3 ~/Documents/code/MCPs/testrail_cli.py case|run|search
```
URL: https://testrail.corp.acronis.com

## Bitbucket CLI
```bash
python3 ~/Documents/code/MCPs/bitbucket_cli.py pr|comments|list|search
```
URL: https://git.acronis.work

## Jira / Confluence (via VM proxy)
```bash
python3 ~/Documents/code/MCPs/jira_cli.py issue|search|confluence|epic|create|sprint-list|sprint-add
```
VM proxy: http://10.146.1.215:9000/mcp

## Sync Windsurf MCP config
```bash
cp ~/Documents/code/MCPs/mcp_config.json ~/.codeium/windsurf/mcp_config.json
```

## Playwright MCP
Local via Node.js. Tools: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_evaluate`, `browser_take_screenshot`.

---

## freelance_search project MCP (in progress)
See `tasks.md` for status. Goal: MCP server to search freelance job boards for QA / automation / Python gigs.
