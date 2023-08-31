## Schema Spec

Project descriptions conform to the following schema:

```
      name (str): name of the project
      web (str): url of the project homepage
      github (str): url of the github repository
      category (str): category of the project, one of: "compiler", "library", "tooling", "documentation", "other", "process"
      origin (str): url of the advisory board proposal that initiated the project
      contributors (List[str]): list of contributors
      process (bool): whether or not this is a process maintained by the Scala Center
      description (str): description of the project
```