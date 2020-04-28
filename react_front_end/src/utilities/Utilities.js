import React from "react";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import { UiForAppError } from "./ui/UiForAppError";

export const toCurrency = (number) => {
  // change to the locale en-US, de-DE
  const formatter = new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
  });
  const v = Number(number).toFixed(2);
  return formatter.format(v);
};

// DAVID use these to make it easier for you https://material-ui.com/customization/breakpoints/

export const isSm = () => {
  //check to see if user resolution is considered "small"
  return useMediaQuery.bind(null, "(max-height:650px)")(); //for iphone 5SE
};

export const CustomUiError = ({ error, type }) => {
  switch (type) {
    case "app":
      return <UiForAppError error={error} />;
    default:
      return null;
  }
};

export const isL = () => {
  //check to see if user resolution is considered "large" (Desktop)
  return useMediaQuery.bind(null, "(min-width:1024px)")();
};

// the next help function
