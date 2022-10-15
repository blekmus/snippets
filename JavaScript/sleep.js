function wait(milliseconds) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve(true);
    }, milliseconds);
  })
}