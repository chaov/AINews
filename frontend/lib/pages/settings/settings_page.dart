import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_cache_manager/flutter_cache_manager.dart';
import '../../providers/providers.dart';

class SettingsPage extends ConsumerStatefulWidget {
  const SettingsPage({super.key});

  @override
  ConsumerState<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends ConsumerState<SettingsPage> {
  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final storage = ref.read(storageServiceProvider);
    final themeMode = ref.watch(themeModeProvider);
    final themeNotifier = ref.read(themeModeProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: ListView(
        children: [
          if (authState.isLoggedIn) ...[
            ListTile(
              leading: const Icon(Icons.person_outline),
              title: const Text('个人中心'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.push('/profile'),
            ),
            const Divider(),
          ],
          ListTile(
            leading: const Icon(Icons.dark_mode_outlined),
            title: const Text('主题'),
            trailing: Text(
              _themeModeLabel(themeMode),
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            onTap: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('选择主题'),
                  content: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      ListTile(
                        title: const Text('跟随系统'),
                        trailing: themeMode == ThemeMode.system
                            ? const Icon(Icons.check, color: Color(0xFFE94560))
                            : null,
                        onTap: () {
                          themeNotifier.setThemeMode('system');
                          Navigator.pop(context);
                        },
                      ),
                      ListTile(
                        title: const Text('浅色模式'),
                        trailing: themeMode == ThemeMode.light
                            ? const Icon(Icons.check, color: Color(0xFFE94560))
                            : null,
                        onTap: () {
                          themeNotifier.setThemeMode('light');
                          Navigator.pop(context);
                        },
                      ),
                      ListTile(
                        title: const Text('深色模式'),
                        trailing: themeMode == ThemeMode.dark
                            ? const Icon(Icons.check, color: Color(0xFFE94560))
                            : null,
                        onTap: () {
                          themeNotifier.setThemeMode('dark');
                          Navigator.pop(context);
                        },
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.notifications_outlined),
            title: const Text('通知'),
            trailing: Switch(
              value: storage.getNotificationsEnabled(),
              onChanged: (value) {
                storage.setNotificationsEnabled(value);
                setState(() {});
              },
            ),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.delete_outline),
            title: const Text('清除缓存'),
            onTap: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('清除缓存'),
                  content: const Text('确定要清除缓存吗？'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('取消'),
                    ),
                    TextButton(
                      onPressed: () async {
                        await DefaultCacheManager().emptyCache();
                        if (context.mounted) {
                          Navigator.pop(context);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('缓存已清除')),
                          );
                        }
                      },
                      child: const Text('确定'),
                    ),
                  ],
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('关于'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'AI News',
                applicationVersion: '1.0.0',
                applicationLegalese: '© 2026 AI News',
              );
            },
          ),
          if (authState.isLoggedIn) ...[
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('退出登录', style: TextStyle(color: Colors.red)),
              onTap: () {
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('退出登录'),
                    content: const Text('确定要退出登录吗？'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('取消'),
                      ),
                      TextButton(
                        onPressed: () {
                          ref.read(authProvider.notifier).logout();
                          Navigator.pop(context);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('已退出登录')),
                          );
                        },
                        child: const Text('确定'),
                      ),
                    ],
                  ),
                );
              },
            ),
          ] else ...[
            const Divider(),
            ListTile(
              leading: const Icon(Icons.login),
              title: const Text('登录'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.push('/login'),
            ),
          ],
        ],
      ),
    );
  }

  String _themeModeLabel(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.light:
        return '浅色';
      case ThemeMode.dark:
        return '深色';
      case ThemeMode.system:
        return '跟随系统';
    }
  }
}
