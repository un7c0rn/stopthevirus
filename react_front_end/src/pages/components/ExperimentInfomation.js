/* eslint-disable no-restricted-globals */
import Button from "@material-ui/core/Button";
import { grey } from "@material-ui/core/colors";
import { AutoRotatingCarousel } from "material-auto-rotating-carousel";
import React, { useState } from "react";
import "./ExperimentInformation.scss";
import Slide from "./ExperimentInformationSlide";

const ExperimentInformation = () => {
  const [state, setState] = useState({});

  const handleSlideButtonClick = (e) => {
    setState({ open: false });
    location.href = "/start-game";
  };

  return (
    <div className="experiment-information-container">
      <Button
        className="button"
        onClick={() => {
          setState({ open: true });
        }}
      >
        What is this?
      </Button>
      <AutoRotatingCarousel
        label="Get started"
        open={state.open}
        onClose={() => {
          setState({ open: false });
        }}
        // onStart={() => {
        //   setState({ open: false });
        // }}
        ButtonProps={{
          style: { visibility: "hidden" },
        }}
        style={{ height: "50vh !important" }}
      >
        <Slide
          buttonClickHandler={handleSlideButtonClick}
          media={
            <img
              src="http://www.icons101.com/icon_png/size_256/id_79394/youtube.png"
              alt="1st slide description"
            />
          }
          mediaBackgroundStyle={{
            backgroundColor: grey[100],
            height: "40%",
          }}
          style={{
            backgroundColor: "#d7d7d7",
            height: "auto",
            minHeight: "100%",
            paddingBottom: "2em",
            overflowX: "hidden",
          }}
          title="Why is this important and what's the social impact?"
          subtitle="It’s Spring 2020 and Coachella, SXSW, the NBA, NHL, MLB and the
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
      youth to stop the virus?"
        />
        <Slide
          buttonClickHandler={handleSlideButtonClick}
          media={
            <img
              src="http://www.icons101.com/icon_png/size_256/id_80975/GoogleInbox.png"
              alt="1st slide description"
            />
          }
          mediaBackgroundStyle={{ backgroundColor: grey[100], height: "40%" }}
          style={{
            backgroundColor: "#d7d7d7",
            height: "auto",
            minHeight: "100%",
            paddingBottom: "2em",
            overflowX: "hidden",
          }}
          title="What inspired this game?"
          subtitle="This social game was inspired by the TV show Survivor (Watch before
      reading more). It's a game based on fun challenges, alliances and
      human psychology. The twist here is that instead of being stranded
      on a deserted island for 30 days, players are &quote;stranded&quote; inside
      their homes. This is important because social distancing, i.e.
      staying home, is the best tool that the youth have right now for
      collectively fighting the epidemic. All challenges in this game are
      designed to incentivize social distancing and spreading awareness.
      Simple activities like making home made cotton based masks can help
      reduce droplet based transmission rates by up to 70% and can be
      turned into social awareness challenges. Young and healthy people
      are at risk and can engage in activities that can increase risk for
      others, so the goal is to create home-based activities that reward
      risk mitigation."
        />
        <Slide
          buttonClickHandler={handleSlideButtonClick}
          media={
            <img
              src="http://www.icons101.com/icon_png/size_256/id_76704/Google_Settings.png"
              alt="1st slide description"
            />
          }
          mediaBackgroundStyle={{ backgroundColor: grey[100], height: "60%" }}
          style={{
            backgroundColor: "#d7d7d7",
            height: "auto",
            minHeight: "100%",
            paddingBottom: "2em",
            overflowX: "hidden",
          }}
          title="What's in it for me?"
          subtitle="Also, since the game is digital and based on social media, we aren't
      limited to the standard 20 players. Everyone can play. With the hope
      of attracting even more players and convincing them to socially
      distance, a donation is required to join and the winner takes all."
        />
      </AutoRotatingCarousel>
    </div>
  );
};

export default ExperimentInformation;
