# V1 — Release

**Depends on:** M4 complete.

**References:** [Features](../features.md) · [Running](../guides/running.md)

Polish, deployment, and long-term maintenance foundations.

---

## Scope

- Mobile responsive layout (responsive tables, swipeable offcanvas)
- Keyboard navigation throughout
- `prefers-reduced-motion` respected
- Dark / light mode toggle persisted in Settings
- Automated backup on schedule (APScheduler, configurable cron)
- SQLite snapshot download (`GET /api/export/sqlite`)
- Docker image + `docker-compose.yml`
- Full deployment guide in [guides/running.md](../guides/running.md)

---

## Release Checklist

- [ ] All M1–M4 acceptance criteria passing
- [ ] No 501 stubs remaining
- [ ] Mobile layout tested on iOS Safari + Android Chrome
- [ ] Keyboard nav: tab order correct, focus visible, Esc closes offcanvas
- [ ] Docker build produces working container from clean pull
- [ ] Seed + round-trip test on fresh install
- [ ] `CHANGELOG.md` written covering M1–V1
- [ ] `docs/guides/running.md` complete and accurate
