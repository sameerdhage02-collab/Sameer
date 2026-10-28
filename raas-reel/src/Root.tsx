import React from 'react';
import {Composition} from 'remotion';
import {Video, TOTAL} from './Video';
export const Root: React.FC = () => (
  <Composition id="WeatherReel" component={Video} durationInFrames={TOTAL} fps={30} width={1080} height={1920} />
);
