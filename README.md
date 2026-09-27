# Independent Premier Padel iCal feed — official FIP source

This repository generates a subscribable `.ics` calendar by reading the **official FIP Premier Padel calendar** and retaining only:

- Premier Padel Major
- Premier Padel P1
- Premier Padel Master Finals

GitHub Actions refreshes the feed once per week and publishes it through GitHub Pages.

## One-time setup

1. Create a new **public GitHub repository** named `premier-padel-fip-calendar`.
2. Upload all files from this folder, keeping `.github/workflows/update.yml` in place.
3. In **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/docs`.
4. Run **Actions → Update Premier Padel calendar → Run workflow** once.
5. Your calendar feed will be:

   `https://YOUR-USERNAME.github.io/premier-padel-fip-calendar/premier-padel.ics`

6. Subscribe to that URL in Apple Calendar.

The feed is generated from FIP's official calendar page rather than from StudyPadel or another calendar provider.

## Notes

- FIP's calendar is explicitly subject to change, so the workflow fetches the current official page instead of hard-coding tournament dates.
- Delayed/postponed events that no longer have dates are naturally excluded until FIP publishes a new dated event.
- Event links point back to the corresponding FIP event page.
