export const toCurrency = number => {
  // change to the locale en-US, de-DE
  const formatter = new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP"
  });
  const v = Number(number).toFixed(2);
  return formatter.format(v);
};

// the next help function
