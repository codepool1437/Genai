"""
Course seed data — 120+ real courses across 20 skill areas.
Each course has a rich `text` field that gets embedded so semantic search works well.
"""

COURSES: list[dict] = [

    # ── Python ───────────────────────────────────────────────────────────────
    {"id": "py-1", "skill": "Python", "title": "Python for Everybody Specialization",
     "platform": "Coursera", "level": "Beginner", "duration": "8 weeks", "free": False,
     "url": "https://www.coursera.org/specializations/python",
     "text": "Python for Everybody teaches Python programming basics, data structures, web scraping, databases, and data visualization. Great for absolute beginners wanting to learn Python for data science or software development."},

    {"id": "py-2", "skill": "Python", "title": "Automate the Boring Stuff with Python",
     "platform": "Udemy / Free Book", "level": "Beginner", "duration": "10 weeks", "free": True,
     "url": "https://automatetheboringstuff.com/",
     "text": "Learn Python by building real automation scripts — file manipulation, web scraping with BeautifulSoup, Excel automation, PDF processing, sending emails, and scheduling tasks."},

    {"id": "py-3", "skill": "Python", "title": "Python Data Science Handbook",
     "platform": "GitHub / O'Reilly", "level": "Intermediate", "duration": "Self-paced", "free": True,
     "url": "https://jakevdp.github.io/PythonDataScienceHandbook/",
     "text": "Comprehensive guide to IPython, NumPy, Pandas, Matplotlib, and Scikit-Learn. Essential reading for anyone using Python for data science or machine learning."},

    {"id": "py-4", "skill": "Python", "title": "100 Days of Code: Python Bootcamp",
     "platform": "Udemy (Angela Yu)", "level": "Beginner", "duration": "100 days", "free": False,
     "url": "https://www.udemy.com/course/100-days-of-code/",
     "text": "Build 100 projects in 100 days with Python. Covers web development with Flask, data science, automation, game development, and APIs."},

    {"id": "py-5", "skill": "Python", "title": "Python OOP — Object-Oriented Programming",
     "platform": "Corey Schafer YouTube", "level": "Intermediate", "duration": "3 weeks", "free": True,
     "url": "https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc",
     "text": "Deep dive into Python object-oriented programming: classes, inheritance, dunder methods, decorators, property, and class/static methods."},

    # ── Machine Learning ──────────────────────────────────────────────────────
    {"id": "ml-1", "skill": "Machine Learning", "title": "Machine Learning Specialization",
     "platform": "Coursera (Andrew Ng)", "level": "Intermediate", "duration": "3 months", "free": False,
     "url": "https://www.coursera.org/specializations/machine-learning-introduction",
     "text": "Andrew Ng's updated ML course covering supervised learning, unsupervised learning, regression, classification, clustering, recommender systems, and reinforcement learning with Python and scikit-learn."},

    {"id": "ml-2", "skill": "Machine Learning", "title": "fast.ai – Practical Deep Learning for Coders",
     "platform": "fast.ai", "level": "Intermediate", "duration": "2 months", "free": True,
     "url": "https://course.fast.ai/",
     "text": "Top-down practical approach to deep learning and machine learning. Covers image classification, NLP, tabular data, collaborative filtering using PyTorch and FastAI library."},

    {"id": "ml-3", "skill": "Machine Learning", "title": "Hands-On Machine Learning with Scikit-Learn & TensorFlow",
     "platform": "O'Reilly Book", "level": "Intermediate", "duration": "Self-paced", "free": False,
     "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/",
     "text": "The definitive ML textbook. Covers end-to-end ML projects, training models, SVM, decision trees, ensemble methods, dimensionality reduction, and neural networks with TensorFlow/Keras."},

    {"id": "ml-4", "skill": "Machine Learning", "title": "Applied Machine Learning in Python",
     "platform": "Coursera (UMich)", "level": "Intermediate", "duration": "6 weeks", "free": False,
     "url": "https://www.coursera.org/learn/python-machine-learning",
     "text": "Applied ML using scikit-learn: classification, regression, feature engineering, model evaluation, cross-validation, pipelines, and more. Part of the Applied Data Science specialization."},

    {"id": "ml-5", "skill": "Machine Learning", "title": "Introduction to Machine Learning — Kaggle",
     "platform": "Kaggle", "level": "Beginner", "duration": "2 weeks", "free": True,
     "url": "https://www.kaggle.com/learn/intro-to-machine-learning",
     "text": "Free beginner friendly ML course on Kaggle. Decision trees, model validation, random forests, XGBoost. Includes hands-on notebooks and competitions."},

    # ── Deep Learning ─────────────────────────────────────────────────────────
    {"id": "dl-1", "skill": "Deep Learning", "title": "Deep Learning Specialization",
     "platform": "Coursera (Andrew Ng)", "level": "Advanced", "duration": "5 months", "free": False,
     "url": "https://www.coursera.org/specializations/deep-learning",
     "text": "5-course specialization covering neural networks, hyperparameter tuning, regularization, optimization, CNNs for computer vision, sequence models, LSTM, attention mechanisms, and transformers."},

    {"id": "dl-2", "skill": "Deep Learning", "title": "Zero to Mastery TensorFlow Developer",
     "platform": "Udemy", "level": "Intermediate", "duration": "3 months", "free": False,
     "url": "https://www.udemy.com/course/tensorflow-developer-certificate-machine-learning-zero-to-mastery/",
     "text": "Complete TensorFlow course for the TensorFlow Developer Certificate. Neural networks, CNNs, NLP with transformers, time series forecasting, transfer learning."},

    {"id": "dl-3", "skill": "Deep Learning", "title": "PyTorch for Deep Learning Bootcamp",
     "platform": "Udemy (Daniel Bourke)", "level": "Intermediate", "duration": "2 months", "free": False,
     "url": "https://www.udemy.com/course/pytorch-for-deep-learning/",
     "text": "Complete PyTorch course covering tensors, autograd, neural network architectures, CNNs, transfer learning, object detection, NLP with transformers, and model deployment."},

    {"id": "dl-4", "skill": "Deep Learning", "title": "MIT 6.S191: Introduction to Deep Learning",
     "platform": "MIT OpenCourseWare", "level": "Advanced", "duration": "6 weeks", "free": True,
     "url": "http://introtodeeplearning.com/",
     "text": "MIT's official deep learning course. Covers deep sequence models, CNNs, GANs, reinforcement learning, and deployment. Includes coding labs in TensorFlow."},

    # ── Data Analysis ─────────────────────────────────────────────────────────
    {"id": "da-1", "skill": "Data Analysis", "title": "Google Data Analytics Professional Certificate",
     "platform": "Coursera", "level": "Beginner", "duration": "6 months", "free": False,
     "url": "https://www.coursera.org/professional-certificates/google-data-analytics",
     "text": "Industry-recognised certificate. Covers data analytics lifecycle, spreadsheets, SQL, Tableau, R programming, and capstone projects. Designed for career changers."},

    {"id": "da-2", "skill": "Data Analysis", "title": "Data Analysis with Python — freeCodeCamp",
     "platform": "freeCodeCamp", "level": "Beginner", "duration": "4 weeks", "free": True,
     "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/",
     "text": "Free certification covering NumPy, Pandas, Matplotlib, Seaborn, and data cleaning. Includes 5 projects: demographic data analysis, medical data visualizer, time series visualiser."},

    {"id": "da-3", "skill": "Data Analysis", "title": "Pandas for Data Analysis",
     "platform": "Kaggle", "level": "Intermediate", "duration": "1 week", "free": True,
     "url": "https://www.kaggle.com/learn/pandas",
     "text": "Hands-on Pandas course: creating DataFrames, indexing, groupby, merging, reshaping, and data cleaning. Perfect preparation for data science competitions."},

    {"id": "da-4", "skill": "Data Analysis", "title": "Data Visualization with Python",
     "platform": "Coursera (IBM)", "level": "Intermediate", "duration": "3 weeks", "free": False,
     "url": "https://www.coursera.org/learn/python-for-data-visualization",
     "text": "Matplotlib, Seaborn, Folium, Plotly, and Dash for creating interactive dashboards and visualizations. Part of IBM Data Science Professional Certificate."},

    # ── Statistics ────────────────────────────────────────────────────────────
    {"id": "st-1", "skill": "Statistics", "title": "Statistics with Python Specialization",
     "platform": "Coursera (UMich)", "level": "Beginner", "duration": "3 months", "free": False,
     "url": "https://www.coursera.org/specializations/statistics-with-python",
     "text": "3-course series: understanding and visualizing data, inferential statistical analysis, and fitting statistical models. Essential for data scientists."},

    {"id": "st-2", "skill": "Statistics", "title": "Khan Academy Statistics & Probability",
     "platform": "Khan Academy", "level": "Beginner", "duration": "Self-paced", "free": True,
     "url": "https://www.khanacademy.org/math/statistics-probability",
     "text": "Free comprehensive statistics course: descriptive statistics, probability, normal distributions, confidence intervals, hypothesis testing, chi-square tests, ANOVA."},

    {"id": "st-3", "skill": "Statistics", "title": "StatQuest with Josh Starmer",
     "platform": "YouTube", "level": "Intermediate", "duration": "Self-paced", "free": True,
     "url": "https://www.youtube.com/c/joshstarmer",
     "text": "Best statistics channel on YouTube. Clearly explains p-values, PCA, t-SNE, linear regression, logistic regression, random forests, and Bayesian statistics with visual intuition."},

    # ── SQL ───────────────────────────────────────────────────────────────────
    {"id": "sql-1", "skill": "SQL", "title": "SQL for Data Science",
     "platform": "Coursera (UC Davis)", "level": "Beginner", "duration": "4 weeks", "free": False,
     "url": "https://www.coursera.org/learn/sql-for-data-science",
     "text": "SQL fundamentals for data scientists: SELECT queries, filtering, aggregations, JOINs, subqueries, views, and data manipulation. Uses SQLite."},

    {"id": "sql-2", "skill": "SQL", "title": "SQLZoo Interactive Tutorial",
     "platform": "sqlzoo.net", "level": "Beginner", "duration": "2 weeks", "free": True,
     "url": "https://sqlzoo.net/",
     "text": "Free interactive SQL tutorial with exercises directly in the browser. Covers SELECT, WHERE, SUM/COUNT, JOIN, subquery, self-join, NULL values, and window functions."},

    {"id": "sql-3", "skill": "SQL", "title": "Advanced SQL — Window Functions & CTEs",
     "platform": "Mode Analytics", "level": "Intermediate", "duration": "2 weeks", "free": True,
     "url": "https://mode.com/sql-tutorial/",
     "text": "Advanced SQL concepts: window functions (ROW_NUMBER, RANK, LAG, LEAD), CTEs, pivoting, performance optimization, indexes, and query planning."},

    {"id": "sql-4", "skill": "SQL", "title": "PostgreSQL Tutorial",
     "platform": "postgresqltutorial.com", "level": "Intermediate", "duration": "3 weeks", "free": True,
     "url": "https://www.postgresqltutorial.com/",
     "text": "Complete PostgreSQL guide: installation, data types, constraints, triggers, stored procedures, transactions, full-text search, JSON support, and performance tuning."},

    # ── Web Development ───────────────────────────────────────────────────────
    {"id": "web-1", "skill": "Web Development", "title": "The Complete Web Developer Bootcamp",
     "platform": "Udemy (Angela Yu)", "level": "Beginner", "duration": "3 months", "free": False,
     "url": "https://www.udemy.com/course/the-complete-web-development-bootcamp/",
     "text": "Most popular web dev course on Udemy. HTML5, CSS3, JavaScript ES6, Bootstrap, React, Node.js, Express, MongoDB, REST APIs, and SQL databases."},

    {"id": "web-2", "skill": "Web Development", "title": "Full Stack Open",
     "platform": "University of Helsinki", "level": "Intermediate", "duration": "4 months", "free": True,
     "url": "https://fullstackopen.com/en/",
     "text": "Free university-level full stack course: React, Redux, Node.js, MongoDB, Express, GraphQL, TypeScript, React Native, and CI/CD. One of the best free resources."},

    {"id": "web-3", "skill": "Web Development", "title": "The Odin Project",
     "platform": "theodinproject.com", "level": "Beginner", "duration": "6 months", "free": True,
     "url": "https://www.theodinproject.com/",
     "text": "Free full-stack curriculum covering HTML, CSS, JavaScript, Git, Node.js, and Ruby on Rails. Project-based learning with a strong community."},

    {"id": "web-4", "skill": "Web Development", "title": "React — The Complete Guide",
     "platform": "Udemy (Maximilian Schwarzmüller)", "level": "Intermediate", "duration": "2 months", "free": False,
     "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
     "text": "Deep dive into React: components, hooks, state management with Redux/Context, React Router, Next.js, TypeScript integration, testing with React Testing Library."},

    {"id": "web-5", "skill": "Web Development", "title": "CS50's Web Programming with Python and JavaScript",
     "platform": "edX (Harvard)", "level": "Intermediate", "duration": "3 months", "free": True,
     "url": "https://cs50.harvard.edu/web/",
     "text": "Harvard's web programming course. HTML, CSS, JavaScript, Git, Python/Django, REST APIs, SQL, testing, CI/CD, scalability, and security. Completely free."},

    # ── Cloud ─────────────────────────────────────────────────────────────────
    {"id": "cloud-1", "skill": "Cloud Computing", "title": "AWS Cloud Practitioner Essentials",
     "platform": "AWS Training", "level": "Beginner", "duration": "6 weeks", "free": True,
     "url": "https://aws.amazon.com/training/learn-about/cloud-practitioner/",
     "text": "Introduction to AWS services: EC2, S3, RDS, Lambda, IAM, CloudWatch, and pricing models. Prepares for the AWS Cloud Practitioner certification exam."},

    {"id": "cloud-2", "skill": "Cloud Computing", "title": "Google Cloud Associate Cloud Engineer",
     "platform": "Coursera", "level": "Intermediate", "duration": "3 months", "free": False,
     "url": "https://www.coursera.org/professional-certificates/cloud-engineering-gcp",
     "text": "Prepare for Google Cloud Associate Cloud Engineer certification. Covers Compute Engine, Kubernetes Engine, Cloud Storage, Cloud SQL, BigQuery, IAM, and VPC networking."},

    {"id": "cloud-3", "skill": "Cloud Computing", "title": "Azure Fundamentals AZ-900",
     "platform": "Microsoft Learn", "level": "Beginner", "duration": "4 weeks", "free": True,
     "url": "https://learn.microsoft.com/en-us/certifications/exams/az-900/",
     "text": "Microsoft Azure fundamentals: cloud concepts, core Azure services, security, privacy, compliance, Azure pricing, and support. Free preparation for the AZ-900 exam."},

    {"id": "cloud-4", "skill": "Cloud Computing", "title": "AWS Solutions Architect Associate",
     "platform": "A Cloud Guru", "level": "Intermediate", "duration": "3 months", "free": False,
     "url": "https://acloudguru.com/course/aws-certified-solutions-architect-associate-saa-c03",
     "text": "Comprehensive SAA-C03 prep: EC2, ECS, EKS, S3, RDS, Aurora, DynamoDB, ElastiCache, SQS, SNS, API Gateway, Lambda, CloudFormation, and security best practices."},

    # ── DevOps ────────────────────────────────────────────────────────────────
    {"id": "devops-1", "skill": "DevOps", "title": "Docker & Kubernetes: The Complete Guide",
     "platform": "Udemy (Stephen Grider)", "level": "Intermediate", "duration": "2 months", "free": False,
     "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/",
     "text": "Complete Docker and Kubernetes course: containers, images, Docker Compose, Kubernetes pods, deployments, services, ingress, Helm, and production deployment on AWS/GCP."},

    {"id": "devops-2", "skill": "DevOps", "title": "90 Days of DevOps",
     "platform": "GitHub (free)", "level": "Intermediate", "duration": "90 days", "free": True,
     "url": "https://github.com/MichaelCade/90DaysOfDevOps",
     "text": "Free open-source DevOps journey covering Linux, networking, Git, containers, Kubernetes, IaC with Terraform, CI/CD with GitHub Actions, monitoring with Prometheus/Grafana."},

    {"id": "devops-3", "skill": "DevOps", "title": "GitHub Actions — CI/CD",
     "platform": "GitHub Learning", "level": "Beginner", "duration": "2 weeks", "free": True,
     "url": "https://skills.github.com/",
     "text": "Learn GitHub Actions for continuous integration and deployment. Build automated workflows, run tests, build Docker images, and deploy to cloud providers."},

    {"id": "devops-4", "skill": "DevOps", "title": "Terraform for Beginners",
     "platform": "freeCodeCamp / HashiCorp",  "level": "Intermediate", "duration": "3 weeks", "free": True,
     "url": "https://developer.hashicorp.com/terraform/tutorials",
     "text": "Infrastructure as Code with Terraform: providers, resources, variables, state management, modules, workspaces, and deploying to AWS, Azure, and GCP."},

    # ── Data Structures & Algorithms ──────────────────────────────────────────
    {"id": "dsa-1", "skill": "Data Structures & Algorithms", "title": "NeetCode 150",
     "platform": "neetcode.io", "level": "Intermediate", "duration": "2 months", "free": True,
     "url": "https://neetcode.io/",
     "text": "150 curated LeetCode problems with video solutions. Arrays, strings, linked lists, trees, graphs, dynamic programming, greedy algorithms. Best resource for coding interviews at FAANG."},

    {"id": "dsa-2", "skill": "Data Structures & Algorithms", "title": "Algorithms Specialization",
     "platform": "Coursera (Stanford)", "level": "Advanced", "duration": "4 months", "free": False,
     "url": "https://www.coursera.org/specializations/algorithms",
     "text": "Stanford's algorithms course: divide and conquer, sorting, searching, randomized algorithms, graph search, shortest paths, data structures, greedy algorithms, dynamic programming, NP-completeness."},

    {"id": "dsa-3", "skill": "Data Structures & Algorithms", "title": "DSA Full Course",
     "platform": "freeCodeCamp YouTube", "level": "Beginner", "duration": "6 hours", "free": True,
     "url": "https://www.youtube.com/watch?v=8hly31xKli0",
     "text": "Free 6-hour DSA course: arrays, linked lists, stacks, queues, hash tables, trees, heaps, graphs, sorting algorithms (bubble, merge, quick, heap sort), and BFS/DFS."},

    {"id": "dsa-4", "skill": "Data Structures & Algorithms", "title": "Grokking Algorithms",
     "platform": "Manning Publications", "level": "Beginner", "duration": "Self-paced", "free": False,
     "url": "https://www.manning.com/books/grokking-algorithms",
     "text": "Illustrated, beginner-friendly book on algorithms: binary search, recursion, quicksort, hash tables, breadth-first search, Dijkstra's algorithm, greedy algorithms, dynamic programming."},

    # ── NLP / GenAI ───────────────────────────────────────────────────────────
    {"id": "nlp-1", "skill": "NLP / GenAI", "title": "Hugging Face NLP Course",
     "platform": "Hugging Face (free)", "level": "Intermediate", "duration": "6 weeks", "free": True,
     "url": "https://huggingface.co/learn/nlp-course/",
     "text": "Official Hugging Face course: transformers, BERT, GPT-2, tokenization, fine-tuning, sequence classification, NER, question answering, summarization, and translation using the Transformers library."},

    {"id": "nlp-2", "skill": "NLP / GenAI", "title": "Building Systems with ChatGPT API",
     "platform": "DeepLearning.AI (free)", "level": "Intermediate", "duration": "1 week", "free": True,
     "url": "https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/",
     "text": "Short course on building LLM-powered applications: chaining prompts, classification, extraction, checking outputs, evaluation. Uses OpenAI API with Python."},

    {"id": "nlp-3", "skill": "NLP / GenAI", "title": "LangChain for LLM Application Development",
     "platform": "DeepLearning.AI (free)", "level": "Intermediate", "duration": "1 week", "free": True,
     "url": "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/",
     "text": "LangChain fundamentals: models, prompts, chains, memory, agents, and tools. Build question-answering systems, chatbots with memory, and document analysis apps."},

    {"id": "nlp-4", "skill": "NLP / GenAI", "title": "LLM Fine-Tuning with LoRA",
     "platform": "Weights & Biases / Hugging Face", "level": "Advanced", "duration": "3 weeks", "free": True,
     "url": "https://huggingface.co/docs/peft/",
     "text": "Fine-tune large language models with LoRA and QLoRA: parameter-efficient fine-tuning, PEFT library, dataset preparation, training on consumer GPUs, and merging adapters."},

    {"id": "nlp-5", "skill": "NLP / GenAI", "title": "Vector Databases and RAG Systems",
     "platform": "DeepLearning.AI (free)", "level": "Intermediate", "duration": "1 week", "free": True,
     "url": "https://www.deeplearning.ai/short-courses/building-and-evaluating-advanced-rag/",
     "text": "Build advanced RAG systems: sentence embeddings, vector databases, similarity search, hybrid retrieval, re-ranking, and evaluating RAG with RAGAS metrics."},

    # ── Computer Vision ───────────────────────────────────────────────────────
    {"id": "cv-1", "skill": "Computer Vision", "title": "Convolutional Neural Networks (DeepLearning.AI)",
     "platform": "Coursera", "level": "Intermediate", "duration": "5 weeks", "free": False,
     "url": "https://www.coursera.org/learn/convolutional-neural-networks",
     "text": "CNNs from scratch: convolutions, pooling, ResNet, Inception, YOLO object detection, face recognition, neural style transfer. Part of Andrew Ng's Deep Learning Specialization."},

    {"id": "cv-2", "skill": "Computer Vision", "title": "OpenCV Python Bootcamp",
     "platform": "freeCodeCamp YouTube", "level": "Beginner", "duration": "5 hours", "free": True,
     "url": "https://www.youtube.com/watch?v=oXlwWbU8l2o",
     "text": "OpenCV with Python: image processing, filtering, edge detection, contours, color spaces, face detection with Haar Cascades, real-time video processing."},

    # ── Mobile Development ────────────────────────────────────────────────────
    {"id": "mob-1", "skill": "Mobile Development", "title": "Flutter & Dart — Complete Guide",
     "platform": "Udemy (Academind)", "level": "Beginner", "duration": "3 months", "free": False,
     "url": "https://www.udemy.com/course/learn-flutter-dart-to-build-ios-android-apps/",
     "text": "Build cross-platform iOS and Android apps with Flutter and Dart. State management with Provider and Riverpod, Firebase integration, animations, and app store deployment."},

    {"id": "mob-2", "skill": "Mobile Development", "title": "React Native — Practical Guide",
     "platform": "Udemy (Maximilian Schwarzmüller)", "level": "Intermediate", "duration": "2 months", "free": False,
     "url": "https://www.udemy.com/course/react-native-the-practical-guide/",
     "text": "Cross-platform mobile development with React Native: navigation, state management with Redux, native device features, push notifications, animations, and deployment to App Store and Play Store."},

    # ── Cybersecurity ─────────────────────────────────────────────────────────
    {"id": "sec-1", "skill": "Cybersecurity", "title": "Google Cybersecurity Professional Certificate",
     "platform": "Coursera", "level": "Beginner", "duration": "6 months", "free": False,
     "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
     "text": "Entry-level cybersecurity certificate by Google. Security operations, network security, Linux, SQL, Python for security, SIEM tools, intrusion detection, and incident response."},

    {"id": "sec-2", "skill": "Cybersecurity", "title": "CompTIA Security+ Prep",
     "platform": "Professor Messer (free)", "level": "Intermediate", "duration": "2 months", "free": True,
     "url": "https://www.professormesser.com/security-plus/sy0-701/sy0-701-video/sy0-701-comptia-security-plus-course/",
     "text": "Free video series for CompTIA Security+ SY0-701: threats, attacks, network security, cryptography, identity management, risk management, and security operations."},

    {"id": "sec-3", "skill": "Cybersecurity", "title": "TryHackMe — Practical Ethical Hacking",
     "platform": "TryHackMe", "level": "Beginner", "duration": "3 months", "free": True,
     "url": "https://tryhackme.com/",
     "text": "Hands-on cybersecurity learning in browser-based labs. Penetration testing, network exploitation, web application hacking, privilege escalation, and CTF challenges."},

    # ── Blockchain / Web3 ─────────────────────────────────────────────────────
    {"id": "bc-1", "skill": "Blockchain", "title": "Blockchain Specialization",
     "platform": "Coursera (UBuffalo)", "level": "Intermediate", "duration": "4 months", "free": False,
     "url": "https://www.coursera.org/specializations/blockchain",
     "text": "Blockchain fundamentals, Ethereum smart contracts with Solidity, decentralized applications, Truffle framework, IPFS, and design patterns."},

    # ── System Design ─────────────────────────────────────────────────────────
    {"id": "sd-1", "skill": "System Design", "title": "Grokking the System Design Interview",
     "platform": "Educative.io", "level": "Advanced", "duration": "6 weeks", "free": False,
     "url": "https://www.educative.io/courses/grokking-the-system-design-interview",
     "text": "System design for software engineering interviews: scalability, load balancing, caching, databases (SQL vs NoSQL), sharding, replication, message queues, microservices, design of Twitter/Uber/Netflix."},

    {"id": "sd-2", "skill": "System Design", "title": "System Design Primer",
     "platform": "GitHub (free)", "level": "Advanced", "duration": "Self-paced", "free": True,
     "url": "https://github.com/donnemartin/system-design-primer",
     "text": "Free open-source system design resource on GitHub. Performance vs scalability, latency vs throughput, CAP theorem, DNS, CDN, load balancers, databases, caches, asynchronism."},

    # ── Software Engineering ──────────────────────────────────────────────────
    {"id": "swe-1", "skill": "Software Engineering", "title": "CS50x — Introduction to Computer Science",
     "platform": "edX (Harvard)", "level": "Beginner", "duration": "3 months", "free": True,
     "url": "https://cs50.harvard.edu/x/",
     "text": "Harvard's introduction to computer science. Scratch, C, Python, SQL, JavaScript, algorithms, data structures, web development, and cybersecurity. Best intro CS course available."},

    {"id": "swe-2", "skill": "Software Engineering", "title": "Clean Code Principles",
     "platform": "Udemy (Uncle Bob)", "level": "Intermediate", "duration": "6 weeks", "free": False,
     "url": "https://www.udemy.com/course/writing-clean-code/",
     "text": "Write maintainable, readable code: naming conventions, functions, comments, error handling, unit testing, refactoring, SOLID principles, and design patterns."},

    {"id": "swe-3", "skill": "Software Engineering", "title": "Git & GitHub Complete Guide",
     "platform": "Udemy", "level": "Beginner", "duration": "2 weeks", "free": False,
     "url": "https://www.udemy.com/course/git-and-github-bootcamp/",
     "text": "Complete Git course: branching, merging, rebasing, cherry-picking, reflogs, GitHub collaboration, pull requests, GitHub Actions, and open source contribution workflow."},

    # ── Data Engineering ──────────────────────────────────────────────────────
    {"id": "de-1", "skill": "Data Engineering", "title": "Data Engineering Zoomcamp",
     "platform": "DataTalks.Club (free)", "level": "Intermediate", "duration": "3 months", "free": True,
     "url": "https://github.com/DataTalksClub/data-engineering-zoomcamp",
     "text": "Free data engineering bootcamp: Docker, Terraform, GCP, Apache Airflow, dbt, Spark, and Kafka. Build end-to-end data pipelines and batch/streaming processing systems."},

    {"id": "de-2", "skill": "Data Engineering", "title": "Apache Spark with Python (PySpark)",
     "platform": "Udemy", "level": "Intermediate", "duration": "6 weeks", "free": False,
     "url": "https://www.udemy.com/course/spark-and-python-for-big-data-with-pyspark/",
     "text": "Big data processing with PySpark: RDDs, DataFrames, Spark SQL, MLlib, Spark Streaming, and deploying Spark on AWS EMR and Databricks."},

    # ── Mathematics for ML ────────────────────────────────────────────────────
    {"id": "math-1", "skill": "Mathematics for ML", "title": "Mathematics for Machine Learning Specialization",
     "platform": "Coursera (Imperial College)", "level": "Intermediate", "duration": "3 months", "free": False,
     "url": "https://www.coursera.org/specializations/mathematics-machine-learning",
     "text": "Math foundations for ML: linear algebra (vectors, matrices, eigenvalues, PCA), multivariate calculus (gradients, chain rule, backpropagation), and PCA applied to datasets."},

    {"id": "math-2", "skill": "Mathematics for ML", "title": "3Blue1Brown — Essence of Linear Algebra",
     "platform": "YouTube (free)", "level": "Beginner", "duration": "4 hours", "free": True,
     "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab",
     "text": "Beautiful visual series on linear algebra: vectors, linear transformations, matrix multiplication, determinants, eigenvectors, and how they relate to machine learning."},

    # ── Product Management ────────────────────────────────────────────────────
    {"id": "pm-1", "skill": "Product Management", "title": "Product Management Fundamentals",
     "platform": "Coursera (UCDavis)", "level": "Beginner", "duration": "4 weeks", "free": False,
     "url": "https://www.coursera.org/learn/product-management",
     "text": "Product management basics: product lifecycle, market research, roadmapping, requirements, agile/scrum, metrics, A/B testing, and stakeholder management."},

    {"id": "pm-2", "skill": "Product Management", "title": "Cracking the PM Interview",
     "platform": "Book", "level": "Intermediate", "duration": "Self-paced", "free": False,
     "url": "https://www.amazon.com/Cracking-PM-Interview-Product-Technology/dp/0984782818",
     "text": "Essential book for product management interviews: product design, estimation, analytical questions, behavioral questions, and case studies from companies like Google, Facebook, Amazon."},

    # ── UI/UX Design ──────────────────────────────────────────────────────────
    {"id": "ux-1", "skill": "UI/UX Design", "title": "Google UX Design Professional Certificate",
     "platform": "Coursera", "level": "Beginner", "duration": "6 months", "free": False,
     "url": "https://www.coursera.org/professional-certificates/google-ux-design",
     "text": "Comprehensive UX design certificate: design thinking, user research, wireframing, prototyping in Figma, usability testing, and portfolio building."},

    {"id": "ux-2", "skill": "UI/UX Design", "title": "Figma UI Design Tutorial",
     "platform": "YouTube / Figma", "level": "Beginner", "duration": "2 weeks", "free": True,
     "url": "https://www.youtube.com/watch?v=FTFaQWZBqQ8",
     "text": "Learn Figma from scratch: frames, components, auto-layout, prototyping, design systems, handoff to developers, and collaborative design workflows."},

    # ── MLOps ─────────────────────────────────────────────────────────────────
    {"id": "mlops-1", "skill": "MLOps", "title": "MLOps Specialization",
     "platform": "Coursera (DeepLearning.AI)", "level": "Advanced", "duration": "4 months", "free": False,
     "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops",
     "text": "Production ML systems: ML pipelines, data validation, feature engineering, model training at scale, hyperparameter tuning, model serving with TensorFlow Serving and TFX, monitoring, and A/B testing."},

    {"id": "mlops-2", "skill": "MLOps", "title": "MLflow for Machine Learning",
     "platform": "Udemy", "level": "Intermediate", "duration": "3 weeks", "free": False,
     "url": "https://www.udemy.com/course/mlflow-for-machine-learning/",
     "text": "MLflow experiment tracking, model registry, artifact storage, and deployment. Integrate with scikit-learn, TensorFlow, and PyTorch for reproducible ML experiments."},
]
