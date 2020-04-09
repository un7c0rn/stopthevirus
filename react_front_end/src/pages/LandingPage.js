import React, { useRef, useEffect, useState } from "react";
import { Button } from "./components/Button";
import { withStyles } from "@material-ui/core";

// put your custom styles in here
const styles = (theme) => ({});

const LandingPage = () => {
  // state
  const [yourStateItem, setYourStateItem] = useState();
  const [buttonLabel1, setButtonLabel1] = useState("PLAY");
  const [buttonLabel2, setButtonLabel2] = useState("INSTUCTIONS");
  const [buttonLabel3, setButtonLabel3] = useState("CREATE A GAME");
  const [buttonLabel4, setButtonLabel4] = useState("SCROLL");
  // refs
  const buttonRef1 = useRef();
  const buttonRef2 = useRef();
  const buttonRef3 = useRef();
  const buttonRef4 = useRef();
  // effect
  useEffect(() => {
    // do something like
    setYourStateItem("#STOPTHEVIRUS");
  }, []);

  const play = (event) => {
    console.log("play");
  };

  const instructions = (event) => {
    console.log("instructions");
  };

  const create = (event) => {
    console.log("create");
  };

  const scroll = (event) => {
    console.log("scroll");
  };

  return (
    <>
      <section>
        <h1>{yourStateItem}</h1>
        {/* <Button ref={buttonRef} label={yourButtonLabel} /> */}
      </section>
      {/* This <section> is the width of the view port */}
      {/* width: 100vw */}
      <section>
        {/* These <sections> below should scroll horizontally left and horizontally right - using a swipe motion */}
        {/* overflow-x: scroll */}
        <section>
          <h1>
            Can a global scale high stakes social game help inspire millions of
            Millennial and Gen-Z individuals across the world to engage in
            social distancing?
          </h1>
        </section>
        <section>
          <h1>why this is important and the social impact</h1>
        </section>
        <section>
          <h1>
            It’s Spring 2020 and Coachella, SXSW, the NBA, NHL, MLB and the
            Tokyo Olympics are cancelled this year. We’re at the height of human
            technology and innovation, but at the same time facing one of the
            most devastating viral pandemics in history. The economy is
            suffering, countries around the world are facing mandatory lockdown
            orders and hospitals are overwhelmed. Despite this, many people are
            still unaware of the seriousness of COVID-19 and actions they can
            take to support our health care professionals such as social
            distancing to flatten the health care demand curve. Reducing the
            doubling rate of COVID-19 by even a few days can have massive
            impact. Can we use a high stakes social game to help inspire the
            youth to stop the virus?
          </h1>
        </section>
        <section>
          <h1>
            This social game was inspired by the TV show Survivor (Watch before
            reading more). It's a game based on fun challenges, alliances and
            human psychology. The twist here is that instead of being stranded
            on a deserted island for 30 days, players are "stranded" inside
            their homes. This is important because social distancing, i.e.
            staying home, is the best tool that the youth have right now for
            collectively fighting the epidemic. All challenges in this game are
            designed to incentivize social distancing and spreading awareness.
            Simple activities like making home made cotton based masks can help
            reduce droplet based transmission rates by up to 70% and can be
            turned into social awareness challenges. Young and healthy people
            are at risk and can engage in activities that can increase risk for
            others, so the goal is to create home-based activities that reward
            risk mitigation.
          </h1>
        </section>
        <section>
          <h1>
            Also, since the game is digital and based on social media, we aren't
            limited to the standard 20 players. Everyone can play. With the hope
            of attracting even more players and convincing them to socially
            distance, a donation is required to join and the winner takes all.
          </h1>
        </section>
      </section>

      <section>
        <Button ref={buttonRef1} label={buttonLabel1} click={play} />
        <Button ref={buttonRef2} label={buttonLabel2} click={instructions} />
        <Button ref={buttonRef3} label={buttonLabel3} click={create} />
        <Button ref={buttonRef4} label={buttonLabel4} click={scroll} />
      </section>
    </>
  );
};

export default withStyles(styles)(LandingPage);
