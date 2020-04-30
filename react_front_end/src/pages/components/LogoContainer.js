import React from "react";
// import { makeStyles } from "@material-ui/core/styles";
import "./LogoContainer.scss";
import { useLocation } from "react-router-dom";

const LogoContainer = ({ children, layout }) => {
  const location = useLocation();

  return (
    <div
      className={
        location.pathname.indexOf("start-game") !== -1
          ? "root row"
          : "root column"
      }
    >
      {children}
    </div>
  );
};
export default LogoContainer;
