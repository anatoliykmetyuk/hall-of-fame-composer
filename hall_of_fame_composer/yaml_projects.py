import os, frontmatter, dotenv, yaml
dotenv.load_dotenv()

SCALACENTER_PROJECTS_PATH = os.getenv("SCALACENTER_PROJECTS_PATH")
OUT_PATH = os.getenv("OUT_PATH")
cache_path = os.path.join(OUT_PATH, "projects.yaml")

def get_file_metadata(path: str):
    with open(path, "r") as f:
        content = frontmatter.load(f)
        return content.metadata

def process_file_metadata(metadata: dict):
    project = {
      "name": metadata["name"],
      "web": metadata["web"],
      "github": metadata["github"],
      "contributors": metadata["contributors"],
      "category": metadata["category"],
      "process": metadata["category"] == "process",
      "description": metadata["description"],
    }
    if "origin" in metadata:
        project["origin"] = metadata["origin"]
    return project

def eligible_project(metadata: dict):
    return (
        metadata["status"] == "Maintenance" or
        metadata["status"] == "Contributors Welcome!" or
        metadata["status"] == "Completed" or
        metadata["status"] == "Active" and metadata["category"] == "process"
    )

def process_projects(path: str):
    projects = []
    for project in os.listdir(path):
        if project.endswith(".md"):
            metadata_raw = get_file_metadata(os.path.join(path, project))
            if eligible_project(metadata_raw):
                metadata = process_file_metadata(metadata_raw)
                projects.append(metadata)
    return projects

def write_yaml_projects():
    projects = process_projects(SCALACENTER_PROJECTS_PATH)
    if not os.path.exists(OUT_PATH):
        os.mkdir(OUT_PATH)
    with open(cache_path, "w") as f:
        yaml.dump(projects, f, sort_keys=False)

def read_yaml_projects(use_cache=False):
    if not use_cache or not os.path.exists(cache_path):
        write_yaml_projects()
    with open(cache_path, "r") as f:
        projects = yaml.load(f, Loader=yaml.FullLoader)
        return projects

if __name__ == "__main__":
    print(read_yaml_projects())
