
import sys
from downloader import load_conf,connect_label_studio,fetch_tasks,save_tasks,download_images
def main():
    conf = load_conf()
    
    client = connect_label_studio(
        conf['url'], 
        conf['api_key'], 
        conf['project_id']
    )
    tasks = fetch_tasks(client, conf['project_id'], conf['only_completed'])

    if not tasks:
        print("  No tasks to save. Exiting.")
        sys.exit(0)
    save_tasks(tasks, conf['output_dir'], conf['project_id'])
    download_images(client)
    print("\n  Download complete.")

if __name__ == "__main__":
    main()