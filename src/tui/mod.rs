use anyhow::Result;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::{Backend, CrosstermBackend},
    layout::{Constraint, Direction, Layout, Alignment},
    style::{Color, Modifier, Style},
    text::Line,
    widgets::{Block, Borders, List, ListItem, ListState, Paragraph, Wrap},
    Terminal,
};
use std::{io, time::Duration};

use crate::github::GitHubFetcher;
use crate::simple;
use crate::complex;

enum AppMode {
    MainMenu,
    SelectSkill(SkillAction),
    Executing,
}

#[derive(Clone, Copy)]
enum SkillAction {
    Install,
    Uninstall,
}

enum OperationMode {
    Simple,
    Complex,
}

struct App {
    mode: AppMode,
    operation_mode: OperationMode,
    main_menu_state: ListState,
    skills_state: ListState,
    skills: Vec<String>,
    messages: Vec<String>,
    should_quit: bool,
}

impl App {
    fn new() -> App {
        let mut main_menu_state = ListState::default();
        main_menu_state.select(Some(0));

        let mut skills_state = ListState::default();
        skills_state.select(Some(0));

        App {
            mode: AppMode::MainMenu,
            operation_mode: OperationMode::Simple,
            main_menu_state,
            skills_state,
            skills: Vec::new(),
            messages: vec!["Welcome to the Agent Harness TUI!".to_string()],
            should_quit: false,
        }
    }

    fn next_main_menu(&mut self) {
        let i = match self.main_menu_state.selected() {
            Some(i) => {
                if i >= 4 {
                    0
                } else {
                    i + 1
                }
            }
            None => 0,
        };
        self.main_menu_state.select(Some(i));
    }

    fn previous_main_menu(&mut self) {
        let i = match self.main_menu_state.selected() {
            Some(i) => {
                if i == 0 {
                    4
                } else {
                    i - 1
                }
            }
            None => 0,
        };
        self.main_menu_state.select(Some(i));
    }

    fn next_skill(&mut self) {
        if self.skills.is_empty() { return; }
        let i = match self.skills_state.selected() {
            Some(i) => {
                if i >= self.skills.len() - 1 {
                    0
                } else {
                    i + 1
                }
            }
            None => 0,
        };
        self.skills_state.select(Some(i));
    }

    fn previous_skill(&mut self) {
        if self.skills.is_empty() { return; }
        let i = match self.skills_state.selected() {
            Some(i) => {
                if i == 0 {
                    self.skills.len() - 1
                } else {
                    i - 1
                }
            }
            None => 0,
        };
        self.skills_state.select(Some(i));
    }

    fn toggle_operation_mode(&mut self) {
        self.operation_mode = match self.operation_mode {
            OperationMode::Simple => OperationMode::Complex,
            OperationMode::Complex => OperationMode::Simple,
        };
    }
}

pub async fn run() -> Result<()> {
    // setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // create app and run it
    let mut app = App::new();
    let res = run_app(&mut terminal, &mut app).await;

    // restore terminal
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        println!("{:?}", err)
    }

    Ok(())
}

async fn run_app<B: Backend + std::io::Write>(terminal: &mut Terminal<B>, app: &mut App) -> Result<()> where <B as Backend>::Error: Send + Sync + 'static {
    let fetcher = GitHubFetcher::new()?;

    app.messages.push("Fetching available skills...".to_string());

    // Attempt to fetch skills, but don't block forever if network fails
    if let Ok(skills) = fetcher.list_skills().await {
        app.skills = skills;
        app.messages.push("Skills loaded.".to_string());
    } else {
        app.messages.push("Failed to load skills.".to_string());
    }

    loop {
        terminal.draw(|f| ui(f, app))?;

        if event::poll(Duration::from_millis(50))? {
            if let Event::Key(key) = event::read()? {
                match app.mode {
                    AppMode::MainMenu => match key.code {
                        KeyCode::Char('q') => app.should_quit = true,
                        KeyCode::Down | KeyCode::Char('j') => app.next_main_menu(),
                        KeyCode::Up | KeyCode::Char('k') => app.previous_main_menu(),
                        KeyCode::Char('m') => app.toggle_operation_mode(),
                        KeyCode::Enter => {
                            if let Some(selected) = app.main_menu_state.selected() {
                                match selected {
                                    0 => { // Init
                                        app.mode = AppMode::Executing;
                                        terminal.draw(|f| ui(f, app))?;

                                        // Suspend TUI
                                        disable_raw_mode()?;
                                        execute!(terminal.backend_mut(), LeaveAlternateScreen, DisableMouseCapture)?;
                                        terminal.show_cursor()?;

                                        let result = match app.operation_mode {
                                            OperationMode::Simple => simple::run_init(&fetcher, true).await,
                                            OperationMode::Complex => complex::run_init(&fetcher, None).await,
                                        };

                                        // Wait for user to read stdout if in complex mode
                                        if let OperationMode::Complex = app.operation_mode {
                                            println!("\nPress Enter to return to TUI...");
                                            let mut buf = String::new();
                                            let _ = io::stdin().read_line(&mut buf);
                                        }

                                        // Resume TUI
                                        enable_raw_mode()?;
                                        execute!(terminal.backend_mut(), EnterAlternateScreen, EnableMouseCapture)?;
                                        terminal.clear()?;

                                        match result {
                                            Ok(_) => app.messages.push("Init successful.".to_string()),
                                            Err(e) => app.messages.push(format!("Init failed: {}", e)),
                                        }
                                        app.mode = AppMode::MainMenu;
                                    }
                                    1 => { // Install Skill
                                        if app.skills.is_empty() {
                                            app.messages.push("No skills available to install.".to_string());
                                        } else {
                                            app.mode = AppMode::SelectSkill(SkillAction::Install);
                                        }
                                    }
                                    2 => { // Uninstall Skill
                                        if app.skills.is_empty() {
                                            app.messages.push("No skills available to uninstall.".to_string());
                                        } else {
                                            app.mode = AppMode::SelectSkill(SkillAction::Uninstall);
                                        }
                                    }
                                    3 => { // Update
                                        app.mode = AppMode::Executing;
                                        terminal.draw(|f| ui(f, app))?;

                                        // Suspend TUI
                                        disable_raw_mode()?;
                                        execute!(terminal.backend_mut(), LeaveAlternateScreen, DisableMouseCapture)?;
                                        terminal.show_cursor()?;

                                        let result = match app.operation_mode {
                                            OperationMode::Simple => simple::run_init(&fetcher, true).await,
                                            OperationMode::Complex => complex::run_init(&fetcher, None).await,
                                        };

                                        // Wait for user to read stdout if in complex mode
                                        if let OperationMode::Complex = app.operation_mode {
                                            println!("\nPress Enter to return to TUI...");
                                            let mut buf = String::new();
                                            let _ = io::stdin().read_line(&mut buf);
                                        }

                                        // Resume TUI
                                        enable_raw_mode()?;
                                        execute!(terminal.backend_mut(), EnterAlternateScreen, EnableMouseCapture)?;
                                        terminal.clear()?;

                                        match result {
                                            Ok(_) => app.messages.push("Update successful.".to_string()),
                                            Err(e) => app.messages.push(format!("Update failed: {}", e)),
                                        }
                                        app.mode = AppMode::MainMenu;
                                    }
                                    4 => { // Quit
                                        app.should_quit = true;
                                    }
                                    _ => {}
                                }
                            }
                        }
                        _ => {}
                    },
                    AppMode::SelectSkill(action) => match key.code {
                        KeyCode::Esc | KeyCode::Char('q') => app.mode = AppMode::MainMenu,
                        KeyCode::Down | KeyCode::Char('j') => app.next_skill(),
                        KeyCode::Up | KeyCode::Char('k') => app.previous_skill(),
                        KeyCode::Enter => {
                            if let Some(selected) = app.skills_state.selected() {
                                if selected < app.skills.len() {
                                    let skill = app.skills[selected].clone();
                                    app.mode = AppMode::Executing;
                                    terminal.draw(|f| ui(f, app))?;

                                    // Suspend TUI
                                    disable_raw_mode()?;
                                    execute!(terminal.backend_mut(), LeaveAlternateScreen, DisableMouseCapture)?;
                                    terminal.show_cursor()?;

                                    let result = match action {
                                        SkillAction::Install => {
                                            match app.operation_mode {
                                                OperationMode::Simple => simple::run_install(&fetcher, &skill, true).await,
                                                OperationMode::Complex => complex::run_install(&fetcher, &skill, None).await,
                                            }
                                        }
                                        SkillAction::Uninstall => {
                                            match app.operation_mode {
                                                OperationMode::Simple => simple::run_uninstall(&fetcher, &skill, true).await,
                                                OperationMode::Complex => complex::run_uninstall(&fetcher, &skill, None).await,
                                            }
                                        }
                                    };

                                    // Wait for user to read stdout if in complex mode
                                    if let OperationMode::Complex = app.operation_mode {
                                        println!("\nPress Enter to return to TUI...");
                                        let mut buf = String::new();
                                        let _ = io::stdin().read_line(&mut buf);
                                    }

                                    // Resume TUI
                                    enable_raw_mode()?;
                                    execute!(terminal.backend_mut(), EnterAlternateScreen, EnableMouseCapture)?;
                                    terminal.clear()?;

                                    let action_str = match action {
                                        SkillAction::Install => "installed",
                                        SkillAction::Uninstall => "uninstalled",
                                    };

                                    match result {
                                        Ok(_) => app.messages.push(format!("Skill '{}' {} successfully.", skill, action_str)),
                                        Err(e) => app.messages.push(format!("Skill operation failed: {}", e)),
                                    }
                                    app.mode = AppMode::MainMenu;
                                }
                            }
                        }
                        _ => {}
                    },
                    AppMode::Executing => {
                        // Ignore input while executing
                    }
                }
            }
        }

        if app.should_quit {
            return Ok(());
        }
    }
}

fn ui(f: &mut ratatui::Frame, app: &mut App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .margin(2)
        .constraints(
            [
                Constraint::Length(3), // Header
                Constraint::Min(5),    // Main Content
                Constraint::Length(6), // Logs
                Constraint::Length(3), // Footer
            ]
            .as_ref(),
        )
        .split(f.area());

    // Header
    let op_mode_str = match app.operation_mode {
        OperationMode::Simple => "Simple (Direct File Modification)",
        OperationMode::Complex => "Complex (Agent Prompt Generation)",
    };

    let header = Paragraph::new(format!(" Agent Harness Utility | Mode: {} ", op_mode_str))
        .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::ALL));
    f.render_widget(header, chunks[0]);

    // Main Content
    match app.mode {
        AppMode::MainMenu | AppMode::Executing => {
            let items = vec![
                ListItem::new("1. Initialize Repository (Init)"),
                ListItem::new("2. Install Skill"),
                ListItem::new("3. Uninstall Skill"),
                ListItem::new("4. Update Harness"),
                ListItem::new("5. Quit"),
            ];

            let list = List::new(items)
                .block(Block::default().title(" Main Menu ").borders(Borders::ALL))
                .highlight_style(Style::default().bg(Color::DarkGray).add_modifier(Modifier::BOLD))
                .highlight_symbol(">> ");

            f.render_stateful_widget(list, chunks[1], &mut app.main_menu_state);
        }
        AppMode::SelectSkill(action) => {
            let items: Vec<ListItem> = app.skills.iter()
                .map(|s| ListItem::new(s.clone()))
                .collect();

            let action_str = match action {
                SkillAction::Install => "Install",
                SkillAction::Uninstall => "Uninstall",
            };

            let list = List::new(items)
                .block(Block::default().title(format!(" Select Skill to {} (Esc to go back) ", action_str)).borders(Borders::ALL))
                .highlight_style(Style::default().bg(Color::DarkGray).add_modifier(Modifier::BOLD))
                .highlight_symbol(">> ");

            f.render_stateful_widget(list, chunks[1], &mut app.skills_state);
        }
    }

    // Logs
    let logs_text: Vec<Line> = app.messages.iter()
        .rev()
        .take(4)
        .map(|m| Line::from(m.clone()))
        .collect();

    let logs = Paragraph::new(logs_text)
        .block(Block::default().title(" Logs ").borders(Borders::ALL))
        .wrap(Wrap { trim: true });
    f.render_widget(logs, chunks[2]);

    // Footer
    let help_text = match app.mode {
        AppMode::MainMenu => "q: Quit | ↑/↓: Navigate | Enter: Select | m: Toggle Simple/Complex Mode",
        AppMode::SelectSkill(_) => "Esc/q: Back | ↑/↓: Navigate | Enter: Confirm",
        AppMode::Executing => "Executing... please wait",
    };

    let footer = Paragraph::new(help_text)
        .style(Style::default().fg(Color::Gray))
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::ALL));
    f.render_widget(footer, chunks[3]);
}
