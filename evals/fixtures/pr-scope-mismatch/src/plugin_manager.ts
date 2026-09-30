export interface Plugin {
  name: string;
  init(): Promise<void>;
  shutdown(): Promise<void>;
}

export class PluginManager {
  private plugins = new Map<string, Plugin>();

  register(plugin: Plugin): void {
    this.plugins.set(plugin.name, plugin);
  }

  async loadAll(): Promise<void> {
    for (const plugin of this.plugins.values()) {
      await plugin.init();
    }
  }
}
