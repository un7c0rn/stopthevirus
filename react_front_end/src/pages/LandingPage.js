import React, { useContext, useEffect, useState } from "react";
import { withStyles } from "@material-ui/core";
import { AppContext } from "../App";

import Footer from "./components/Footer";
import { makeStyles } from "@material-ui/core/styles";
import LandingPageHeaderLogoSvg from "./components/LandingPageHeaderLogoSvg";
import LandingPageInformation from "./components/LandingPageInformation";
import AppTitle from "./components/AppTitle";
import TriangleLogo from "./components/TriangleLogo";

const useStyles = makeStyles((theme) => ({
  root: {
    background: theme.background,
    color: "white",
    height: "100vh",
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-start",
  },
}));

const LandingPage = () => {
  const classes = useStyles();

  const { blurUi } = useContext(AppContext);

  const [blur, setBlur] = useState(false);

  useEffect(() => {
    setBlur(blurUi);
  }, [blurUi]);

  return (
    <>
      <section className={classes.root}>
        <AppTitle />
        <TriangleLogo removeLogo={true} />
        <LandingPageInformation />
        <Footer />
      </section>
    </>
  );
};

export default withStyles(useStyles)(LandingPage);
