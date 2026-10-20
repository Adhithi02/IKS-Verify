import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { ClaimChip } from "./ClaimChip";
import { TrustMeter } from "./TrustMeter";

test("renders claim verdict", () => {
  render(
    <ClaimChip
      claim={{ text: "A claim", citations: [], supporting_verse_ids: [], verdict: "SUPPORTED", rationale: "Evidence" }}
    />,
  );
  expect(screen.getByText("SUPPORTED")).toBeTruthy();
});

test("renders trust score and breakdown", () => {
  render(
    <TrustMeter
      score={0.75}
      claims={[
        { text: "a", citations: [], supporting_verse_ids: [], verdict: "SUPPORTED" },
        { text: "b", citations: [], supporting_verse_ids: [], verdict: "UNVERIFIABLE" },
      ]}
    />,
  );
  expect(screen.getByLabelText("Trust score 75%")).toBeTruthy();
  expect(screen.getByText(/Supported 1/)).toBeTruthy();
});
