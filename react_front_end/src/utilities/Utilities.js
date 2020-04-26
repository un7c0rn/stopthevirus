import useMediaQuery from "@material-ui/core/useMediaQuery";

export const toCurrency = number => {
  // change to the locale en-US, de-DE
  const formatter = new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP"
  });
  const v = Number(number).toFixed(2);
  return formatter.format(v);
};

export const isSm = () => {
  //check to see if user resolution is considered "small"
  return useMediaQuery.bind(null, "(max-height:650px)")();//for iphone 5SE
};

export const isL = () => {
  //check to see if user resolution is considered "large" (Desktop)
  return useMediaQuery.bind(null, "(max-width:1024px)")();
};

// the next help function
