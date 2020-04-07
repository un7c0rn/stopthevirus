import React, { useRef, useEffect, useState } from "react";
import { Button } from "./components/Button";
import { withStyles } from "@material-ui/core";

// put your custom styles in here
const styles = theme => ({});

const InstructionsPage = () => {
  // state
  const [yourStateItem, setYourStateItem] = useState();
  const [yourButtonLabel, setYourButtonLabel] = useState("CREATE A GAME");
  // refs
  const buttonRef = useRef();
  // effect
  useEffect(() => {
    // do something like
    setYourStateItem("#STOPTHEVIRUS");
    // log the ref innerText
    console.log(buttonRef.current.innerText);
  }, []);

  return (
    <>
      <section>
        <h1>{yourStateItem}</h1>
      </section>
      <section>
        <h1>Instructions</h1>
      </section>
      {/* This <section> is the width of the view port */}
      {/* width: 100vw */}
      <section>
        {/* These <sections> below should scroll horizontally left and horizontally right - using a swipe motion */}
        {/* overflow-x: scroll */}
        <section>
          <h1>
            Players signup with a group of friends as teawm, or can be
            automatically placed on a team.
          </h1>
        </section>
        <section>
          <h1>All teams are grouped into one of two tribes.</h1>
        </section>
        <section>
          <h1>
            A new social distancinbg challenge is posted on TikTok and emailed
            to players.
          </h1>
        </section>
        <section>
          <h1>
            Challenge entries i.e TikTok posts tagged #STOTHEVIRUS are gathered
            until the challenge expires. For example, 1 day.
          </h1>
        </section>
        <section>
          <h1>
            All entries are scored for both tribes. The final score is the
            average score i.e. average likes per page view for each player entry
            in the entire tribe.
          </h1>
        </section>
        <section>
          <h1>
            The tribe with the least amount of points goes to tribal council.
            Every sub-team within the tribe must vote out one member.
          </h1>
        </section>
        <section>
          <h1>
            As tribes get smaller, teams are automatically combined, until there
            are only a few finalists remaining.
          </h1>
        </section>
        <section>
          <h1>
            Once there are only two finalists remaining, players that have been
            voted out previously now vote for the winner.
          </h1>
        </section>
        <section>
          <h1>Winner is announced and receives prize.</h1>
        </section>
      </section>
      <section>
        <Button ref={buttonRef} label={yourButtonLabel} />
      </section>
    </>
  );
};

export default withStyles(styles)(InstructionsPage);
