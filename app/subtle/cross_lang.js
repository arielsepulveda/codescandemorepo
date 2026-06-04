async function loadProfile() {
  const r = await fetch("/api/me?user_id=" + currentUserId());
  const data = await r.json();
  if (data.is_admin) {
    showAdminPanel();
  } else {
    showRegularPanel();
  }
}

function currentUserId() { return new URLSearchParams(location.search).get("u") || "0"; }
function showAdminPanel()   { document.body.classList.add("admin"); }
function showRegularPanel() { /* ... */ }
