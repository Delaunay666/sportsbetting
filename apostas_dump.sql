PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE apostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT NOT NULL,
                competicao TEXT NOT NULL,
                equipa_casa TEXT NOT NULL,
                equipa_fora TEXT NOT NULL,
                tipo_aposta TEXT NOT NULL,
                odd REAL NOT NULL,
                valor_apostado REAL NOT NULL,
                resultado TEXT DEFAULT 'Pendente',
                lucro_prejuizo REAL DEFAULT 0.0,
                notas TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , tipster_id INTEGER, fonte_tip TEXT, timestamp TEXT, tipster TEXT DEFAULT 'Próprio');
CREATE TABLE configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO "configuracoes" VALUES('saldo_inicial','0.0','2025-08-24 17:47:53');
CREATE TABLE historico_banca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                saldo REAL NOT NULL,
                movimento REAL NOT NULL,
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
CREATE TABLE permissoes_utilizador (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilizador_id INTEGER,
                permissao TEXT NOT NULL,
                concedida BOOLEAN DEFAULT 1,
                data_concessao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (utilizador_id) REFERENCES utilizadores (id)
            );
INSERT INTO "permissoes_utilizador" VALUES(1,1,'criar_apostas',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(2,1,'editar_apostas',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(3,1,'eliminar_apostas',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(4,1,'ver_apostas',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(5,1,'ver_relatorios',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(6,1,'exportar_relatorios',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(7,1,'relatorios_avancados',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(8,1,'configurar_sistema',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(9,1,'gerir_utilizadores',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(10,1,'configurar_seguranca',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(11,1,'importar_dados',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(12,1,'exportar_dados',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(13,1,'backup_sistema',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(14,1,'ver_previsoes',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(15,1,'treinar_modelos',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(16,1,'configurar_ml',1,'2025-08-26 17:15:03');
INSERT INTO "permissoes_utilizador" VALUES(17,2,'criar_apostas',1,'2025-08-26 17:51:36');
INSERT INTO "permissoes_utilizador" VALUES(18,2,'editar_apostas',1,'2025-08-26 17:51:36');
INSERT INTO "permissoes_utilizador" VALUES(19,2,'ver_apostas',1,'2025-08-26 17:51:36');
INSERT INTO "permissoes_utilizador" VALUES(20,2,'ver_relatorios',1,'2025-08-26 17:51:36');
INSERT INTO "permissoes_utilizador" VALUES(21,2,'ver_previsoes',1,'2025-08-26 17:51:36');
CREATE TABLE risk_alerts (
                    id TEXT PRIMARY KEY,
                    tipo TEXT NOT NULL,
                    severidade TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    data_detecao TEXT NOT NULL,
                    valor_envolvido REAL,
                    recomendacao TEXT,
                    ativo BOOLEAN DEFAULT 1,
                    data_resolucao TEXT
                );
CREATE TABLE risk_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    data_detecao TEXT NOT NULL,
                    severidade REAL,
                    valor_envolvido REAL,
                    contexto TEXT
                );
CREATE TABLE sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilizador_id INTEGER,
                token_sessao TEXT UNIQUE NOT NULL,
                data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_expiracao TIMESTAMP,
                ativo BOOLEAN DEFAULT 1,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (utilizador_id) REFERENCES utilizadores (id)
            );
INSERT INTO "sessoes" VALUES(1,1,'uOJkVeWgyryecsjN4GutKBTtEr2Ezcd1KTDX-fyIyQA','2025-08-26 17:46:25','2025-08-27T02:46:25.676261',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(2,2,'Pxw7aMSxrNX06qDoxTpEw6F8pLiUI1cl8mCyW3vKbc4','2025-08-26 17:51:47','2025-08-27T02:51:47.851174',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(3,1,'Yrg_d6dP7bhijRWxVDvPK1VEdpbOGrJ5YujdQwmaaRM','2025-08-26 18:26:43','2025-08-27T03:26:43.082854',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(4,1,'uEVGhzigMGiKHHFcr6cVBTKUPFQT1Wg1OlYz60zMWqo','2025-08-26 18:34:10','2025-08-27T03:34:10.917945',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(5,1,'JSulBb5Ddxn51Hk0deeHTU92kowz1S74iJI3BPl-U48','2025-08-26 18:41:25','2025-08-27T03:41:25.254746',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(6,1,'UAPtK93M3pKidDVi5n2zKcC4RotIdHl_sLCk5qrwJsw','2025-08-26 18:51:17','2025-08-27T03:51:17.529333',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(7,1,'9o90KYOxFuYFsDol5kJ3cmVTsOqy2oatn7P-Y7YHcts','2025-08-26 19:01:10','2025-08-27T04:01:10.648375',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(8,1,'G39mksNoY8UlegBwBYKGtQfNQ28EljdRvvrLQcBO37U','2025-08-26 20:11:32','2025-08-27T05:11:32.380645',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(9,1,'XUgbs1V7ykHKaEoWMAnS41gEE7tWtFO_TJ3pbPpo82U','2025-08-26 20:25:00','2025-08-27T05:25:00.292389',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(10,1,'pq1EfHzWPrlJ-wV9jZUlnO5wb8A4ZVyzT54J3Mv1Z6U','2025-08-26 20:33:33','2025-08-27T05:33:33.667997',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(11,1,'CFbccqCRMpdbyPvW1m7l5zN3-LA4DBJ8dhqa9ohO-Wg','2025-08-26 20:40:18','2025-08-27T05:40:18.808692',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(12,1,'OhW3M7Aj7RqcQjlZW00PhNBfu6H2HFHHBc3kdkGxr0E','2025-08-26 20:47:15','2025-08-27T05:47:15.655505',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(13,1,'DPnKMcjzJCXorHT2quxCqSqYPK2wExxa7ivvm3FtDS4','2025-08-26 20:51:41','2025-08-27T05:51:41.486212',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(14,1,'1D_41VhAdLiWLPH9oOtvH6oi9_Qx1esX9RahkSUXIks','2025-08-26 20:52:03','2025-08-27T05:52:03.092149',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(15,1,'nPRC6VYsdpf4mZ23y3kCETFeAa4lFyj24qJNVfL8O-0','2025-08-26 21:02:04','2025-08-27T06:02:04.752656',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(16,1,'32pNMNLr72LS3LtH52gB4OvKiyw6FEfCufsmW6W4lfw','2025-08-26 21:22:58','2025-08-27T06:22:58.473179',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(17,1,'Wy9GT82xoE8T_qNxeCNESSWvd3CeypavTEnKZk5Zd6c','2025-08-26 21:28:57','2025-08-27T06:28:57.076221',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(18,1,'wJCj3RAeHXUx2Ddk85P497OtXFijPdAwSDRE-NbdrSY','2025-08-26 21:51:49','2025-08-27T06:51:49.204493',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(19,1,'daX9PlktbmUm6wwMrSSO5871dM4rKWa6Y8w_ax-i94A','2025-08-26 21:59:11','2025-08-27T06:59:11.117066',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(20,1,'7HuA3IEAJScKfuznXzMfZ-VYAncyNDySAEhN9IainA8','2025-08-26 22:04:58','2025-08-27T07:04:58.493497',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(21,1,'LoIfFP9xQh_0enLw8ezshfB3FQjzE-bK1dtX-E8nMSo','2025-08-26 22:10:55','2025-08-27T07:10:55.914597',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(22,1,'MN2S66M9kWRCEiKd1tY5EdB4k2G6Eyi2VQ8AyCpiuC4','2025-08-26 23:50:45','2025-08-27T08:50:45.281273',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(23,1,'x7CsTGc51yftU5_tMRFBj4whD01TQVEhiZqvX-LPdXk','2025-08-27 06:00:52','2025-08-27T15:00:52.403474',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(24,1,'gcmhdxSJisUzEcZcTDpoXX1mfy-Ng6y56fsjpkB9Jmo','2025-08-27 16:34:54','2025-08-28T01:34:54.591208',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(25,1,'LFFf_zyV3pmvZWQYwxDkYzVEKL6gbSyp4c0pQKT6S-s','2025-08-27 16:45:53','2025-08-28T01:45:53.788049',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(26,1,'PGd3_m0t_rCiEAvSM40pQ8JzCP_imT5htifAJSmxErg','2025-08-27 17:19:51','2025-08-28T02:19:51.424644',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(27,1,'OsP7H7ZZsm7AKm8r_DJz9mdNtFGJjugVl9OQnmZLNRw','2025-08-27 18:45:40','2025-08-28T03:45:40.271813',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(28,1,'2bBLFQbblYn7ZU0N-3fxo4K66UFYoJW0rZCoDwXc9Iw','2025-08-27 19:23:21','2025-08-28T04:23:21.721031',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(29,1,'8vXWvG47u_ugUSdW9T73ppdBoB0r0HAY1TdkI4u9O90','2025-08-27 19:41:56','2025-08-28T04:41:56.106606',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(30,1,'FyEvtCA1xdgCyQbuNKFkIf2kzMJYoDApP2Wt41jyRrk','2025-08-27 20:35:46','2025-08-28T05:35:46.664898',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(31,1,'R_LKVX5BXVGLsnOFv-nCheXwytqDpVGEpDL3OXCtbpM','2025-08-27 22:01:38','2025-08-28T07:01:38.611610',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(32,1,'9CBNytpKz5CEv7IWnqcdlW9hp_HwwAqDw95onmndT_E','2025-08-27 22:24:15','2025-08-28T07:24:15.474445',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(33,2,'cSLfvhn5QPEwUHRlZn0dyYXa0xkhw9XOye0yO0ihup8','2025-08-27 22:43:30','2025-08-28T07:43:30.291193',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(34,1,'3mWAjzoaCOvDhaXi53DYr226nLGDEYBlicqllw1wU3o','2025-08-28 17:16:41','2025-08-29T02:16:41.980586',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(35,3,'237nXchGVMd_73qE8bjtPzYc132V0xZKd6GPGzDA64k','2025-08-28 17:33:16','2025-08-29T02:33:16.275821',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(36,3,'aLeTtVyoqHaW-1D9Bt07egv4LqxdottEeFcAQouXo5U','2025-08-28 20:18:20','2025-08-29T05:18:20.334042',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(37,3,'OJ5N8Ai_huEgaAEBvrz72iaRQUj3H5Av9McCrlxqQDc','2025-08-29 17:53:00','2025-08-30T02:53:00.021215',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(38,3,'EUOaUBglfEb75SzUixF_SbIu5netGdwv7YhC3s5__ME','2025-08-29 19:33:23','2025-08-30T04:33:23.660904',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(39,3,'UNTnYT78RRX_Bp3X0Y5v5sllaBFCnrZQe81JFWcPd1E','2025-08-29 19:40:55','2025-08-30T04:40:55.906615',1,'localhost','Desktop App');
INSERT INTO "sessoes" VALUES(40,3,'4VNJifkDB5ersRSnwlAzdeK43k0hHJxmqnBBO-l3sWg','2025-08-29 21:12:35','2025-08-30T06:12:35.169286',1,'localhost','Desktop App');
CREATE TABLE tipster_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipster_id INTEGER,
                    data TEXT NOT NULL,
                    win_rate REAL,
                    roi REAL,
                    total_tips INTEGER,
                    lucro_acumulado REAL,
                    FOREIGN KEY (tipster_id) REFERENCES tipsters (id)
                );
CREATE TABLE tipsters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    fonte TEXT NOT NULL,
                    categoria TEXT,
                    data_registo TEXT NOT NULL,
                    ativo BOOLEAN DEFAULT 1,
                    notas TEXT,
                    rating REAL DEFAULT 0.0,
                    confiabilidade TEXT DEFAULT 'Novo'
                );
CREATE TABLE utilizadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                tipo_utilizador TEXT NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP,
                tentativas_login INTEGER DEFAULT 0,
                bloqueado_ate TIMESTAMP,
                configuracoes TEXT DEFAULT '{}'
            );
INSERT INTO "utilizadores" VALUES(3,'admin','admin@apostas.local','4e1c6099280606abcca3c35ab187ed1e1f7a5010bf5cde679066318294f05ed1','f8cbc448e8f75b0869c96c4913a02bdb4b168a076d8a9b49bae1997bd53ababd','admin',1,'2025-08-26 17:15:03','2025-08-29 21:12:35',0,NULL,'{}');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('historico_banca',63);
INSERT INTO "sqlite_sequence" VALUES('apostas',136);
INSERT INTO "sqlite_sequence" VALUES('utilizadores',3);
INSERT INTO "sqlite_sequence" VALUES('permissoes_utilizador',21);
INSERT INTO "sqlite_sequence" VALUES('sessoes',40);
COMMIT;
