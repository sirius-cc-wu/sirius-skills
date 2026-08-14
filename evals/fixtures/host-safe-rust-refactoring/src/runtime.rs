/// Focused handle for the local UDS runtime seam.
#[derive(Debug, PartialEq, Eq)]
pub struct UdsRuntimeHandle {
    running: bool,
}

impl UdsRuntimeHandle {
    /// Creates a prepared UDS runtime handle.
    pub fn prepared() -> Self {
        Self { running: false }
    }

    /// Marks the focused UDS runtime as started.
    pub fn start(mut self) -> Self {
        self.running = true;
        self
    }

    /// Reports whether the focused UDS runtime started.
    pub fn is_running(&self) -> bool {
        self.running
    }
}

/// Focused handle for the local DoIP runtime seam.
#[derive(Debug, PartialEq, Eq)]
pub struct DoipRuntimeHandle {
    running: bool,
}

impl DoipRuntimeHandle {
    /// Creates a prepared DoIP runtime handle.
    pub fn prepared() -> Self {
        Self { running: false }
    }

    /// Marks the focused DoIP runtime as started.
    pub fn start(mut self) -> Self {
        self.running = true;
        self
    }

    /// Reports whether the focused DoIP runtime started.
    pub fn is_running(&self) -> bool {
        self.running
    }
}
