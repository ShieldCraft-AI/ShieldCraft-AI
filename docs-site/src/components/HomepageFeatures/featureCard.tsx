import type { ReactNode } from "react";

export type FeatureCard = {
    title: string;
    Svg: React.ComponentType<React.ComponentProps<'svg'>>;
    description: ReactNode;
};
