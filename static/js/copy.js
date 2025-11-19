function copyEmail(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.select();
  el.setSelectionRange(0, 99999);
  navigator.clipboard.writeText(el.value).then(() => {
    alert("Email copied to clipboard");
  }).catch(() => {
    alert("Copy failed, please copy manually");
  });
}
