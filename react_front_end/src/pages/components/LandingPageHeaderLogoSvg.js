import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import { ReactComponent as Svg } from "./svg/vir-us.logo.svg";
import "./LandingPageHeaderLogoSvg.scss";
import LandingPageSocialMediaButtons from "./LandingPageSocialMediaButtons";

const useStyles = makeStyles((theme) => ({
  root: {},
}));

export const Logo = () => {
  return <Svg />;
};

const LandingPageHeaderLogoSvg = () => {
  const classes = useStyles();

  return (
    <header className="header">
      <div className="logo-container">
        <Logo />
      </div>
      <LandingPageSocialMediaButtons />
    </header>
  );
};

export default withStyles(useStyles)(LandingPageHeaderLogoSvg);
