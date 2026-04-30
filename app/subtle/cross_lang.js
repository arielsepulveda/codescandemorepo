// The frontend half of the cross_lang bug.
//
// Reads the JSON the Python backend produced and decides whether to show
// admin UI. The check is idiomatic JS — but the contract assumes a JSON
// boolean, while the backend ships a string. Both files together = bypass.

async function loadProfile() {
  const r = await fetch("/api/me?user_id=" + currentUserId());
  const data = await r.json();
  // ❌ data.is_admin is "false" or "true" — a string. Both are truthy.
  // This branch executes for every user.
  if (data.is_admin) {
    showAdminPanel();
  } else {
    showRegularPanel();
  }
}

function currentUserId() { return new URLSearchParams(location.search).get("u") || "0"; }
function showAdminPanel()   { document.body.classList.add("admin"); }
function showRegularPanel() { /* ... */ }
