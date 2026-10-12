# Put Vietnamese Driving Theory Test on GitHub

The folder `vietnamese-driving-theory` is the repository root. Run Git commands **inside this folder**, not in the surrounding VDT folder. The project name contains no spaces, but the parent path does, so keep the path in quotes.

## 1. Create an empty repository

Sign in to GitHub and open <https://github.com/new>. Name the repository `vietnamese-driving-theory`. Choose Public if you want everyone to access the quiz. Leave **Add a README**, **Add .gitignore**, and **Choose a license** unselected; these files are already present or require a separate licensing decision. Create the repository and copy its HTTPS URL.

## 2. Push the project

Open PowerShell and run these commands one at a time:

```powershell
cd "C:\Users\liamh\OneDrive\Desktop\Ai folders\VDT\vietnamese-driving-theory"
git init
git add .
git status
git commit -m "Initial Vietnamese Driving Theory Test release"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/vietnamese-driving-theory.git
git push -u origin main
```

Replace `YOUR-USERNAME` and the repository name in the remote URL as needed. Check `git status` before committing; the official PDF should not appear. GitHub may open a browser for sign-in. If `origin` already exists, run `git remote set-url origin YOUR-REPOSITORY-URL`, then `git push -u origin main`.

## 3. Publish the playable website

In the GitHub repository, open **Settings → Pages**. Under **Build and deployment**, select **Deploy from a branch**, branch **main**, folder **/(root)**, then **Save**. Wait for GitHub to display the site URL. Its form is usually `https://YOUR-USERNAME.github.io/REPOSITORY-NAME/`. Add the URL to the repository's About section so visitors can play without downloading anything.

## 4. Offer the ZIP download

The `Vietnamese-Driving-Theory-Test-v1.0.0.zip` file is in the surrounding `VDT` folder, **outside** this Git repository. On the repository page, open **Releases → Create a new release**. Choose a new tag `v1.0.0`, enter `Vietnamese Driving Theory Test v1.0.0` as the title, and attach `C:\Users\liamh\OneDrive\Desktop\Ai folders\VDT\Vietnamese-Driving-Theory-Test-v1.0.0.zip`. Wait for the upload to finish, then publish the release. People can download and extract the ZIP to run the quiz offline. Keep the ZIP out of the Git repository; releases hold downloadable packages.

GitHub's current help pages: [adding local code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github), [publishing from a branch](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), and [managing releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
