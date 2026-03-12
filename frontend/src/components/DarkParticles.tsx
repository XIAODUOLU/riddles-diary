import { useMemo, useEffect } from "react";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { ISourceOptions } from "@tsparticles/engine";

interface DarkParticlesProps {
  isAnimating: boolean;
}

export default function DarkParticles({ isAnimating }: DarkParticlesProps) {
  useEffect(() => {
    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    });
  }, []);

  const options: ISourceOptions = useMemo(
    () => ({
      background: {
        color: {
          value: "transparent",
        },
      },
      fpsLimit: 60,
      particles: {
        number: {
          value: 150,
          density: {
            enable: true,
            width: 700,
            height: 700,
          },
        },
        color: {
          value: ["#1a0a2e", "#2d1b4e", "#4a1f6e", "#6b2d8f", "#8b3fa8", "#0a0a14", "#14141e"],
        },
        shape: {
          type: ["circle", "triangle", "star"],
        },
        opacity: {
          value: { min: 0.4, max: 0.9 },
          animation: {
            enable: true,
            speed: 1.5,
            sync: false,
          },
        },
        size: {
          value: { min: 1, max: 5 },
          animation: {
            enable: true,
            speed: 3,
            sync: false,
          },
        },
        move: {
          enable: true,
          speed: { min: 1, max: 4 },
          direction: "none",
          random: true,
          straight: false,
          outModes: {
            default: "out",
          },
          attract: {
            enable: true,
            rotateX: 800,
            rotateY: 1400,
          },
        },
        links: {
          enable: true,
          distance: 150,
          color: "#4a1f6e",
          opacity: 0.25,
          width: 1,
        },
        shadow: {
          enable: true,
          color: "#6b2d8f",
          blur: 8,
        },
        twinkle: {
          particles: {
            enable: true,
            frequency: 0.05,
            opacity: 1,
          },
        },
      },
      interactivity: {
        detectsOn: "canvas",
        events: {
          resize: {
            enable: true,
          },
        },
      },
      detectRetina: true,
    }),
    []
  );

  if (!isAnimating) return null;

  return (
    <div className="dark-particles-container">
      <Particles
        id="tsparticles"
        options={options}
      />
    </div>
  );
}
