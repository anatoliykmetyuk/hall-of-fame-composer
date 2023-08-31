import dotenv, os, yaml
dotenv.load_dotenv()

OUT_PATH = os.getenv("OUT_PATH")
in_file = os.path.join(OUT_PATH, 'gs_projects.yaml')
out_file = os.path.join(OUT_PATH, 'categorised.yaml')

def categorise_projects(projects: dict) -> dict:
  categories = {}
  for project in projects:
    category = project['category']
    if category not in categories:
      categories[category] = { 'name': category.capitalize(), 'projects': [] }
    del project['category']
    categories[category]['projects'].append(project)
  return categories

def process_projects():
  with open(in_file, 'r') as f:
    projects = yaml.safe_load(f)
  categories = categorise_projects(projects)
  with open(out_file, 'w') as f:
    yaml.dump(categories, f, sort_keys=False)

if __name__ == '__main__':
  process_projects()
