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
  return useMediaQuery.bind(null, "(max-height:650px)")();//for iphone 5SE
};

// the next help function
