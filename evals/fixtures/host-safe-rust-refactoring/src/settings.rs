/// Immutable endpoint settings selected for one validation run.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ValidationSettings {
    doip_port: u16,
    uds_socket: String,
}

impl ValidationSettings {
    /// Creates settings for an isolated validation run.
    pub fn isolated(doip_port: u16, uds_socket: impl Into<String>) -> Self {
        Self {
            doip_port,
            uds_socket: uds_socket.into(),
        }
    }

    /// Returns the selected DoIP port.
    pub fn doip_port(&self) -> u16 {
        self.doip_port
    }

    /// Returns the selected UDS socket path.
    pub fn uds_socket(&self) -> &str {
        &self.uds_socket
    }
}
