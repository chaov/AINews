import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/providers.dart';
import '../../widgets/news_card.dart';
import '../../widgets/category_tab.dart';
import '../../widgets/loading.dart';

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(newsListProvider.notifier).loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    final newsListAsync = ref.watch(newsListProvider);
    final categoriesAsync = ref.watch(categoryProvider);
    final selectedCategory = ref.watch(selectedCategoryProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI News'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () {
              final isLoggedIn = ref.read(authProvider).isLoggedIn;
              if (isLoggedIn) {
                context.push('/profile');
              } else {
                context.push('/login');
              }
            },
          ),
        ],
      ),
      body: Column(
        children: [
          categoriesAsync.when(
            data: (categories) => CategoryTab(
              categories: categories,
              selectedCategory: selectedCategory,
              onCategorySelected: (category) {
                ref.read(selectedCategoryProvider.notifier).state = category;
                ref.read(newsListProvider.notifier).loadNews(category: category, refresh: true);
              },
            ),
            loading: () => const SizedBox(height: 50),
            error: (_, __) => const SizedBox(height: 50),
          ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: () async {
                await ref.read(newsListProvider.notifier).refresh(
                  category: selectedCategory,
                );
              },
              child: newsListAsync.when(
                data: (newsList) {
                  if (newsList.isEmpty) {
                    return ListView(
                      children: const [
                        SizedBox(height: 200),
                        Icon(Icons.article_outlined, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text('暂无资讯', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
                      ],
                    );
                  }

                  final hasMore = ref.read(newsListProvider.notifier).hasMore;

                  return ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: newsList.length + 1,
                    itemBuilder: (context, index) {
                      if (index == newsList.length) {
                        if (hasMore) {
                          return const Padding(
                            padding: EdgeInsets.all(16),
                            child: Center(child: CircularProgressIndicator()),
                          );
                        }
                        return const SizedBox.shrink();
                      }

                      final news = newsList[index];
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: NewsCard(
                          news: news,
                          onTap: () {
                            context.push('/news/${news.id}');
                          },
                        ),
                      );
                    },
                  );
                },
                loading: () => const Loading(),
                error: (error, _) => ListView(
                  children: [
                    const SizedBox(height: 200),
                    const Icon(Icons.error_outline, size: 64, color: Colors.red),
                    const SizedBox(height: 16),
                    Text('加载失败: $error', textAlign: TextAlign.center),
                    const SizedBox(height: 16),
                    Center(
                      child: ElevatedButton(
                        onPressed: () {
                          ref.read(newsListProvider.notifier).refresh();
                        },
                        child: const Text('重试'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
