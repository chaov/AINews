import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/providers.dart';
import '../../widgets/news_card.dart';
import '../../widgets/loading.dart';

class SearchPage extends ConsumerStatefulWidget {
  const SearchPage({super.key});

  @override
  ConsumerState<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends ConsumerState<SearchPage> {
  final _searchController = TextEditingController();
  final _focusNode = FocusNode();

  @override
  void dispose() {
    _searchController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _onSearch() {
    final query = _searchController.text.trim();
    if (query.isNotEmpty) {
      ref.read(searchNewsProvider.notifier).search(query);
      _focusNode.unfocus();
    }
  }

  @override
  Widget build(BuildContext context) {
    final searchResultsAsync = ref.watch(searchNewsProvider);

    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: _searchController,
          focusNode: _focusNode,
          decoration: InputDecoration(
            hintText: '搜索资讯...',
            border: InputBorder.none,
            suffixIcon: IconButton(
              icon: const Icon(Icons.search),
              onPressed: _onSearch,
            ),
          ),
          textInputAction: TextInputAction.search,
          onSubmitted: (_) => _onSearch(),
        ),
      ),
      body: searchResultsAsync.when(
        data: (results) {
          if (_searchController.text.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.search, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('输入关键词搜索资讯', style: TextStyle(color: Colors.grey)),
                ],
              ),
            );
          }

          if (results.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.search_off, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  Text(
                    '未找到 "${_searchController.text}" 相关资讯',
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: results.length,
            itemBuilder: (context, index) {
              final news = results[index];
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
        error: (error, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text('搜索失败: $error'),
            ],
          ),
        ),
      ),
    );
  }
}
