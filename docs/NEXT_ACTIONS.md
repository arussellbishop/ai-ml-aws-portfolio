# Next actions — portfolio system

The public portfolio is deployed and browser-verified. The source is versioned at [GitHub](https://github.com/arussellbishop/ai-ml-aws-portfolio), and the live dashboard is [CloudFront](https://d2ac9c4k7eb96p.cloudfront.net/dashboard.html).

Remaining work, in priority order:

1. Create one signed run manifest and complete a clean restore test.
2. Decide whether Telegram stays draft-only or receives explicitly approved bot credentials and one non-sensitive health-message test.
3. Add labelled citation precision, recall and freshness tests to RAG.
4. Run the hybrid capture-to-paper-ledger pipeline with zero exchange writes.
5. Deploy the AWS operational layer: versioned S3 snapshots, EventBridge, idempotent workers, SQS dead-letter handling, CloudWatch alarms and restore checks.
6. Finish CRAN/Air Marshal research screening, MSc data-boundary updates and the employer application pack.

Finance remains paper/advisory-only, robotics remains edge-supervised, and Telegram remains dry-run until their explicit safety and evidence gates pass.
