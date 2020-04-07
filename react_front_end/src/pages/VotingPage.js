import React, { useRef, useEffect, useState } from "react";
import { Button } from "./components/Button";
import { withStyles } from "@material-ui/core";
import VoteItem from "./components/VoteItem";

// put your custom styles in here
const styles = theme => ({});

const generateTeamMemberList = teamMemberData => {
  // replace with details of the team member
  return teamMemberData.map((data, index) => {
    // replace dummy url with data.url
    return (
      <VoteItem
        key={`vote-item-key-${index}`}
        url={`/images/round-profile-pic.png`}
        name={`${data.name}`}
        id={data.id}
      />
    );
  });
};

const VotingPage = () => {
  // state
  const [yourStateItem, setYourStateItem] = useState();
  const [yourButtonLabel, setYourButtonLabel] = useState("Lift off 🚀");
  const [challengeName, setChallengeName] = useState();
  const [teamMemberData, setTeamMemberData] = useState();
  // refs
  const buttonRef = useRef();
  // effect
  useEffect(() => {
    // do something like
    setYourStateItem("#STOPTHEVIRUS");
    // log the ref innerText
    console.log(buttonRef.current.innerText);
  }, []);

  // get data from service
  useEffect(() => {
    // do something like
    setChallengeName("wash your hands");
    // dummy data
    const data = [
      {
        id: "FS-01",
        name: "First & last name",
        url: "/images/round-profile-pic.png"
      },
      {
        id: "FS-01",
        name: "First & last name",
        url: "/images/round-profile-pic.png"
      },
      {
        id: "FS-01",
        name: "First & last name",
        url: "/images/round-profile-pic.png"
      },
      {
        id: "FS-01",
        name: "First & last name",
        url: "/images/round-profile-pic.png"
      },
      {
        id: "FS-01",
        name: "First & last name",
        url: "/images/round-profile-pic.png"
      }
    ];
    // set the team member data
    setTeamMemberData(data);
  }, []);

  return (
    <>
      <section>
        <h1>{yourStateItem}</h1>
        {/* <Button ref={buttonRef} label={yourButtonLabel} /> */}
      </section>
      <section>
        <h1>{`Challenge: ${challengeName}`}</h1>
      </section>
      {/* The generateTeamMemberList function returns a list of <li> */}
      <section>
        {teamMemberData && <ul>{generateTeamMemberList(teamMemberData)}</ul>}
      </section>
      <Button ref={buttonRef} label={yourButtonLabel} />
    </>
  );
};

export default withStyles(styles)(VotingPage);
