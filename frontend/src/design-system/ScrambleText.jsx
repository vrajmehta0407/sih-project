import React, { useEffect, useState } from 'react';

const CHARS = '0123456789ABCDEFabcdef!@#$%^&*()_+-=';

export const ScrambleText = ({
  text = '',
  duration = 1.2,
  className = '',
  trigger = true,
  onComplete,
}) => {
  const [displayText, setDisplayText] = useState('');

  useEffect(() => {
    if (!trigger || !text) {
      setDisplayText(text);
      return;
    }

    const length = text.length;
    let iteration = 0;
    const totalFrames = duration * 30; // 30fps
    const charsPerFrame = length / totalFrames;

    const interval = setInterval(() => {
      iteration++;
      const revealedCount = Math.floor(iteration * charsPerFrame);

      let scrambled = '';
      for (let i = 0; i < length; i++) {
        if (i < revealedCount) {
          scrambled += text[i];
        } else if (text[i] === ' ') {
          scrambled += ' ';
        } else {
          scrambled += CHARS[Math.floor(Math.random() * CHARS.length)];
        }
      }

      setDisplayText(scrambled);

      if (revealedCount >= length) {
        clearInterval(interval);
        setDisplayText(text);
        if (onComplete) onComplete();
      }
    }, 1000 / 30);

    return () => clearInterval(interval);
  }, [text, duration, trigger, onComplete]);

  return <span className={`font-mono ${className}`}>{displayText}</span>;
};
export default ScrambleText;
