/* eslint-disable no-restricted-globals */
import React from "react";
import "./LogoContainer.scss";

const LogoContainer = ({ children }) => {
  return (
    <div
      className={
        location.pathname.indexOf("start-game") !== -1
          ? "root-container row"
          : "root-container column"
      }
    >
      {children}
    </div>
  );
};
export default LogoContainer;
