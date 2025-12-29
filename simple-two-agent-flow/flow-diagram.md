# Two-Agent Flow Diagram

```mermaid
graph TD
    START([START]) --> answer[answer_node<br/>Generate/Refine Answer]
    
    answer --> |Updates: answer, iteration++| critique[critique_node<br/>Evaluate & Score]
    
    critique --> |Updates: score, feedback| decision{should_continue<br/>Check: score >= 9?<br/>iteration >= 4?}
    
    decision -->|score < 9 AND<br/>iteration < 4| answer
    decision -->|score >= 9 OR<br/>iteration >= 4| END([END])
    
    style START fill:#90EE90
    style END fill:#FFB6C1
    style answer fill:#87CEEB
    style critique fill:#DDA0DD
    style decision fill:#FFD700
```

## State Flow Through Nodes

```mermaid
sequenceDiagram
    participant Start
    participant Answer as answer_node
    participant Critique as critique_node
    participant Decision as should_continue
    participant End
    
    Start->>Answer: State: {question, answer="", feedback="", score=0, iteration=0}
    Answer->>Answer: LLM generates initial answer
    Answer->>Critique: State: {question, answer=<new>, iteration=1}
    Critique->>Critique: LLM evaluates & scores
    Critique->>Decision: State: {score=<0-10>, feedback=<critique>}
    
    alt score >= 9 OR iteration >= 4
        Decision->>End: Terminate
    else Continue loop
        Decision->>Answer: Loop back with feedback
        Answer->>Answer: LLM refines using feedback
        Answer->>Critique: State: {answer=<refined>, iteration++}
        Critique->>Decision: Updated score & feedback
    end
```

## Data Structure Evolution

```mermaid
graph LR
    subgraph "Initial State"
        S1[question: str<br/>answer: ''<br/>feedback: ''<br/>score: 0<br/>iteration: 0]
    end
    
    subgraph "After answer_node"
        S2[question: str<br/>answer: <generated><br/>feedback: ''<br/>score: 0<br/>iteration: 1]
    end
    
    subgraph "After critique_node"
        S3[question: str<br/>answer: <same><br/>feedback: <critique><br/>score: <0-10><br/>iteration: 1]
    end
    
    subgraph "After Loop (if continued)"
        S4[question: str<br/>answer: <refined><br/>feedback: <critique><br/>score: <0-10><br/>iteration: 2]
    end
    
    S1 -->|answer_node| S2
    S2 -->|critique_node| S3
    S3 -->|Loop back| S4
    S4 -.->|Repeat until<br/>score >= 9 or<br/>iteration >= 4| S3
    
    style S1 fill:#E6F3FF
    style S2 fill:#FFE6E6
    style S3 fill:#E6FFE6
    style S4 fill:#FFF6E6
```

