use host_safe_rust_refactoring::{
    runtime::{DoipRuntimeHandle, UdsRuntimeHandle},
    settings::ValidationSettings,
};

#[test]
fn isolated_settings_then_preserve_selected_endpoint_and_socket() {
    let settings = ValidationSettings::isolated(15000, "/tmp/run-1/uds.sock");

    assert_eq!(settings.doip_port(), 15000);
    assert_eq!(settings.uds_socket(), "/tmp/run-1/uds.sock");
}

#[test]
fn focused_runtime_handles_then_report_local_startup() {
    let uds = UdsRuntimeHandle::prepared().start();
    let doip = DoipRuntimeHandle::prepared().start();

    assert!(uds.is_running());
    assert!(doip.is_running());
}
