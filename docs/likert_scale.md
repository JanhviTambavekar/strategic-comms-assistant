# Likert Scale Configuration

This file defines the Likert scale used for human evaluation of generated strategies.

## Scale Options

The following 5-point Likert scale is used for all evaluation statements:

1. **Strongly Disagree**
2. **Disagree**
3. **Neither Agree nor Disagree**
4. **Agree**
5. **Strongly Agree**

## Usage

These options are used in the human evaluation form. The form separately records
ratings for the generated strategy and for the service/process experience; the
two sets of scores must not be combined into one overall score.

## Customization

To modify the Likert scale:

1. Change the scale options below
2. Adjust the `LIKERT_SCALE` list in the application code to match
3. Ensure the number of scale points matches across all evaluation statements

## Current Scale

- Point 1: Strongly Disagree
- Point 2: Disagree
- Point 3: Neither Agree nor Disagree
- Point 4: Agree
- Point 5: Strongly Agree
