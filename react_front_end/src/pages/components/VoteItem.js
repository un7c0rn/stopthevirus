import React, { useRef, useEffect, useState } from "react";
import { Button } from "../components/Button";
import { withStyles } from "@material-ui/core";

const styles = theme => ({});

const VoteItem = ({ url, name, id }) => {
  const [yourButtonLabel, setYourButtonLabel] = useState("Vote off 🚀");
  // refs
  const buttonRef = useRef();

  useEffect(() => {
    // do something
  }, []);

  const click = event => {
    // do something
    console.log(`vote out team member with ID ${id}`);
  };

  return (
    <>
      <li>
        <img src={url} alt="profile pic" width="30" height="30" />
        <p>name</p>
        <Button ref={buttonRef} label={yourButtonLabel} click={click} />
      </li>
    </>
  );
};

export default withStyles(styles)(VoteItem);
