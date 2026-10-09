@'
# NetSage AI - Project Demo Script

## Introduction

Hello, I am Ananthakrishnan, and this is my Cisco internship project, NetSage AI.

NetSage AI is an AI-assisted Cisco network troubleshooting system designed to support network engineers in identifying configuration and connectivity faults.

The system uses a local Qwen3 8B large language model through Ollama and combines AI diagnosis with structured network evidence, deterministic evaluation, and human-in-the-loop review.

## Project Overview

The project contains 42 unique network troubleshooting cases covering multiple networking fault categories.

Each case contains structured information such as network symptoms, topology details, verification results, diagnostic commands, command outputs, and expected fault categories.

## Case Demonstration

This demonstration uses Case C043, an ACL-related network fault.

In this scenario, PC1 can reach its VLAN 10 gateway but cannot communicate with a server located in VLAN 20.

The system presents structured evidence including the network symptom, topology, verification results, diagnostic commands, and configuration output.

The evidence shows an access control list containing a deny rule that blocks communication between the PC and the server.

## AI Diagnosis

Based on the supplied evidence, the local Qwen3 model generates a structured diagnosis.

For Case C043, the AI correctly identifies the fault category as ACL.

The diagnosis includes:

- Fault category
- Confidence score
- Root cause
- OSI layer
- Networking concept
- Supporting evidence
- Next diagnostic command
- Safe recommended fix

## Human-in-the-Loop Review

AI output is not treated as an autonomous final decision.

A human reviewer can review the AI diagnosis and accept, edit, or reject the recommendation.

This ensures that NetSage AI functions as a decision-support system while maintaining human oversight.

## Responsible AI

The project includes five documented human correction records.

These records demonstrate cases where AI predictions required human correction or review.

The Responsible AI workflow supports evidence-based validation and accountability.

## Dashboard and Evaluation

The NetSage AI dashboard provides an overview of system performance.

The final evaluation dataset contains 42 unique cases.

Results:

- Total Cases: 42
- Correct Predictions: 40
- Incorrect Predictions: 2
- Accuracy: 95.24%

The dashboard also provides visual representations of fault categories and evaluation results.

## Packet Tracer Demonstration

The project includes nine Cisco Packet Tracer files representing baseline and selected network fault scenarios.

These practical scenarios demonstrate network behavior and provide supporting environments for troubleshooting and verification.

For the demonstrated ACL scenario, the source device can reach its local gateway while communication with the destination server fails due to the ACL configuration.

## Testing

The project includes deterministic evaluation logic and batch evaluation scripts.

Regression testing was also performed on seven selected cases, with all seven producing correct results.

## Conclusion

NetSage AI combines local large language model inference, structured network evidence, deterministic evaluation, human-in-the-loop review, Responsible AI correction logging, and Cisco Packet Tracer scenarios.

The final implementation achieved an accuracy of 95.24 percent across 42 unique troubleshooting cases.

The project demonstrates how AI can assist network troubleshooting while maintaining evidence-based reasoning and human oversight.
'@ | Set-Content .\script.md -Encoding UTF8