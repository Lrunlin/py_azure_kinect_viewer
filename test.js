function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
(async () => {
  for (let index = 0; index < 350; index++) {
    await fetch(`http://127.0.0.1:3000/capture?preview_mode=0`).catch(() => {});
    console.log(index);
  }
})();
