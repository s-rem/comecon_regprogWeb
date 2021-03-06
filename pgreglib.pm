#!/usr/bin/perl
package pgreglib;
use strict;
use warnings;
use Encode qw/ encode decode /;
use Net::SMTP;

#### 大会独自項目 定数定義
{
package main;
use Sys::Hostname;
our %CONDEF_CONST = (
    'CONNAME'   => '米魂',
    'CONPERIOD' => '2014-2015',
    'FULLNAME'  => '第54回日本SF大会 米魂',
    'ENTADDR'   => 'program@comecon.jp',
    'ENVFROM'   => 'program-return@comecon.jp',
    'PGSTAFF'   => 'program-operater@comecon.jp',
    'MIMENAME'  => '=?ISO-2022-JP?B?GyRCQmgbKEI1NBskQjJzRnxLXBsoQlNGGyRCQmcycRsoQiAbJEJKRjoyPEI5VDBRMHcycRsoQg==?=',
        # '第54回日本SF大会 米魂実行委員会' をMIME化
    'MIMEPGSG'  => '=?ISO-2022-JP?B?GyRCSkY6MjRrMmg8dUlVGyhC?=',
        # '米魂企画受付' をMIME化
    'SPREGNUM1' => '2015DIRECTPGREGIST082930',  # 直接申込jump
    'SPREGNUM2' => '2015DIRECTMAILCHEC082930',  # 直接申込jump&FinalMail確認
    'SPREGNUM3' => '2015MAILBODYCHECK082930',   # FirstMail確認
    'DEVENV'    => hostname =~ /s-rem.jp/ ? 1 : undef,
);
}

#### 企画登録情報 テーブル定義
# CGI値変換テーブル
my %pg_kind_cnv = (         # 企画種別table
    'K-A1'  => '講演',
    'K-A2'  => 'パネルディスカッション',
    'K-A3'  => '講座',
    'K-A4'  => '上映',
    'K-A5'  => '座談会',
    'K-A6'  => 'お茶会',
    'K-A7'  => 'ゲーム',
    'K-B1'  => 'コンサート',
    'K-C1'  => '展示',
    'K-D1'  => '印刷物発行',
    'K-E1'  => '投票',
    'K-X1'  => 'その他',
);
my %pg_place_cnv = (        # 希望場所table
    'P-N'   => '特になし',
    'P-C1'  => '会議室',
    'P-H1'  => '小ホール(300人)',
    'P-P1'  => '一般公開エリア',
    'P-X1'  => 'その他',
);
my %pg_layout_cnv = (       # レイアウトtable
    '0' => 'シアター',
    '1' => 'スクール',
    '2' => 'ロの字',
    '3' => '島組',
    '9' => 'その他',
);
my %pg_time_cnv = (         # 希望日時table
    'T-N'       => '特になし',
    'T-1any'    => '29日(土)のどこでも',
    'T-1am'     => '29日(土)午前',
    'T-1pm'     => '29日(土)午後',
    'T-1ngt'    => '29日(土)夜(パーティ後)',
    'T-2any'    => '30日(日)のどこでも',
    'T-2am'     => '30日(日)午前',
    'T-2pm'     => '30日(日)午後',
    'T-wday'    => '両日',
    'T-X1'      => 'その他',
);
my %pg_koma_cnv = (         # 希望コマ数table
    'TK-1'  => '１コマ(90分+準備30分)',
    'TK-2'  => '２コマ(210分+準備30分)',
    'TK-A'  => '終日',
    'TK-X1' => 'その他',
);
my %pg_ninzu_cnv = (        # 予想参加者table
    'TN-0'  => '不明',
    'TN-1'  => '20人まで',
    'TN-2'  => '50人まで',
    'TN-3'  => '100人まで',
    'TN-4'  => '200人まで',
    'TN-5'  => '200人超',
);
my %pg_naiyou_k_cnv = (     # 内容事前公開table
    'CX-0'  => '事前公開可',
    'CX-1'  => '事前公開不可',
);
my %pg_kiroku_kb_cnv = (    # リアルタイム公開table
    'CX-0'  => 'UST等動画を含む全て許可',
    'CX-1'  => 'twitter等テキストと静止画公開可',
    'CX-2'  => 'テキストのみ公開可',
    'CX-3'  => '公開不可',
    'CX-9'  => 'その他',
);
my %pg_kiroku_ka_cnv = (    # 事後公開table
    'CX-0'  => 'UST等動画を含む全て許可',
    'CX-1'  => 'blog等テキストと静止画公開可',
    'CX-2'  => 'テキストのみ公開可',
    'CX-3'  => '公開不可',
    'CX-9'  => 'その他',
);
my %motikomi_cnv = (   # 持ち込む/持ち込まないtable
    '0' => '持ち込む',
    '1' => '持ち込まない',
);
my %av_v_cnv = (            # 持ち込み映像機器映像接続形式table
    'hdmi'      => 'HDMI',
    'svideo'    => 'S-Video',
    'rca'       => 'RCAコンポジット(黄)',
    'other'     => 'その他',
);
my %av_a_cnv = (            # 持ち込み映像機器音声接続形式table
    'none'  => '不要',
    'tsr'   => 'ステレオミニ(3.5mmTSR)',
    'rca'   => 'RCAコンポジット(赤白)',
    'other' => 'その他',
);
my %pc_v_cnv = (            # 持ち込みPC映像接続形式table
    'none'  => '接続しない',
    'hdmi'  => 'HDMI',
    'vga'   => 'D-Sub15(VGA)',
    'other' => 'その他',
);
my %pc_a_cnv = (            # 持ち込みPC音声接続形式table
    'none'      => '不要',
    'svideo'    => 'ステレオミニ(3.5mmTSR)',
    'rca'       => 'RCAコンポジット(赤白)',
    'other'     => 'その他',
);
my %lan_cnv = (             # ネット接続形式table
    'none'  => '接続しない',
    'lan'   => '有線(RJ-45)',
    'wifi'  => '無線',
    'other' => 'その他',
);
my %pg_enquete_cnv = (      # 企画経験table
    '0' => '初めて',
    '1' => '昨年に続いて2回目',
    '2' => '継続して3〜5回目',
    '3' => 'ひさしぶり',
    '4' => '6回目以上',
);
my %ppn_youdo_cnv = (   # 自身出演table
    '0' => 'する',
    '1' => 'しない',
);
my %ppn_con_cnv = (     # 出演交渉table
    'PP-A'  => '交渉を大会に依頼',
    'PP-B1' => '出演了承済',
    'PP-B2' => '交渉中',
    'PP-B3' => '未交渉',
);
my %ppn_grq_cnv = (     # ゲスト申請table
    'PP-A'  => 'する',
    'PP-B'  => 'しない',
);

### HTMLテンプレート置き換え定義
# 単純置き換え パラメータ名配列
my @org_pname = (
    'p1_name', 'email', 'reg_num', 'tel', 'fax', 'cellphone',
    'pg_name', 'pg_name_f', 'pg_naiyou', 'fc_other_naiyou',
    'fc_mochikomi', 'pg_badprog',
    'fc_comment',
);

# テーブル変換 パラメータテーブル
#   key: パラメータ名
#   value[0]:変換テーブル
#   value[1]:その他内容パラメータ名
my %tbl_pname = (
    'pg_kind'       => [ \%pg_kind_cnv,         'pg_kind2', ],
    'pg_place'      => [ \%pg_place_cnv,        'pg_place2', ],
    'pg_layout'     => [ \%pg_layout_cnv,       'pg_layout2', ],
    'pg_time'       => [ \%pg_time_cnv,         'pg_time2', ],
    'pg_koma'       => [ \%pg_koma_cnv,         'pg_koma2', ],
    'pg_ninzu'      => [ \%pg_ninzu_cnv,        undef, ],
    'pg_naiyou_k'   => [ \%pg_naiyou_k_cnv,     undef, ],
    'pg_kiroku_kb'  => [ \%pg_kiroku_kb_cnv,    undef, ],
    'pg_kiroku_ka'  => [ \%pg_kiroku_ka_cnv,    undef, ],
    'pg_enquete'    => [ \%pg_enquete_cnv,      undef, ],
);
# 使用する/しない パラメータテーブル
#   key: パラメータ名
#   value: 本数パラメータ名
my %useunuse_pname = (
    'wbd'   =>  undef,
    'mic'   =>  'miccnt',
    'mic2'  =>  'mic2cnt',
    'mon'   =>  undef,
    'dvd'   =>  undef,
    'syo'   =>  undef,
);

# 持ち込む/持ち込まない パラメータテーブル
#   key: パラメータ名
#   value: パラメータテーブル
#       key:パラメータ名
#       value[0]:変換テーブル
#       value[1]:その他内容パラメータ名
#       value[2]:注釈
my %motikomi_pname = (
    'fc_vid'    => {
        # 持ち込み映像機器映像接続形式
        'av-v'  => [ \%av_v_cnv,    'av-v_velse',   '映像接続', ],
        # 持ち込み映像機器音声接続形式
        'av-a'  => [ \%av_a_cnv,    'av-a_velse',   '音声接続', ],
    },
    'fc_pc'     => {
        # 持ち込みPC映像接続形式
        'pc-v'  => [ \%pc_v_cnv,    'pc-v_velse',   '映像接続', ],
        'pc-a'  => [ \%pc_a_cnv,    'pc-a_velse',   '音声接続', ],
    },
);

# ネット接続テーブル変換 パラメータテーブル
#   PC持ち込み時のみ変換するため、別テーブルとする
#   key: パラメータ名
#   value[0]:変換テーブル
#   value[1]:その他内容パラメータ名
my %lan_pname = (
    'lan'   => [ \%lan_cnv, 'pc-l_velse', ],
);

## チェックテーブル定義
# 必須項目テーブル
#   入力項目名 => TMPL変数名
my %needs_tbl = (
    # 主催者情報
    'p1_name'   => 'C_P1_NAME',         # 名前
    'email'     => 'C_CO_EMAIL',        # メールアドレス
    'reg_num'   => 'C_CO_REG_NUMBER',   # 参加登録番号
                                    # 電話番号、FAX番号、携帯番号は省略可能
    # 企画情報
    'pg_name'   => 'C_CO_PG_NAME',      # 企画名称
    'pg_name_f' => 'C_CO_PG_NAME_F',    # 企画名称フリガナ
    'pg_kind'   => 'C_CO_PG_KIND',      # 企画種別
    'pg_place'  => 'C_CO_PG_PLACE',     # 希望場所
    'pg_layout' => 'C_CO_PG_PLACE',     # 希望場所レイアウト
    'pg_time'   => 'C_CO_PG_TIME',      # 希望日時
    'pg_koma'   => 'C_CO_PG_KOMA',      # 希望コマ数
    'pg_ninzu'  => 'C_CO_PG_NINZU',     # 予想参加者
    'pg_naiyou' => 'C_CO_PG_NAIYOU',    # 内容説明
    'pg_naiyou_k'   => 'C_CO_PG_NAIYOU',    # 内容説明
    'pg_kiroku_kb'  => 'C_CO_PG_KIROKU_KB', # リアルタイム公開
    'pg_kiroku_ka'  => 'C_CO_PG_KIROKU_KA', # 事後公開
    'pg_enquete'    => 'C_CO_PG_ENQUETE',   # 企画を立てるのは
    'youdo'     => 'C_CO_PG_YOUDO',     # 申込者の出演
);
# 本数チェックテーブル (0より大)
# 条件変数名 => [ チェック変数名, TMPL変数名 ]
my %count_tbl = (
    'mic'       => [ 'miccnt',  'C_CO_PG_KIZAI', ],
    'mic2'      => [ 'mic2cnt', 'C_CO_PG_KIZAI', ],
);
# fc_vid必須項目テーブル
my %fc_vid_needs_tbl = (
    'av-v'  => 'C_CO_PG_KIZAI',
    'av-a'  => 'C_CO_PG_KIZAI',
);
# fc_pc必須項目テーブル
my %fc_pc_needs_tbl = (
    'pc-v'  => 'C_CO_PG_KIZAI',
    'pc-a'  => 'C_CO_PG_KIZAI',
    'lan'   => 'C_CO_PG_KIZAI',
);
# 条件付き必須チェックテーブル
#   条件変数名 => [ 条件値, チェック変数名, TMPL変数名 ]
my %cond_tbl = (
    'pg_kind'   =>  [ 'K-X1',  'pg_kind2',   'C_CO_PG_KIND', ],
    'pg_place'  =>  [ 'P-X1',  'pg_place2',  'C_CO_PG_PLACE', ],
    'pg_layout' =>  [ '9',     'pg_layout2', 'C_CO_PG_PLACE', ],
    'pg_time'   =>  [ 'T-X1',  'pg_time2',   'C_CO_PG_TIME', ],
    'pg_koma'   =>  [ 'TK-X1', 'pg_koma2',   'C_CO_PG_KOMA', ],
);
# 条件付き値固定チェックテーブル
#   条件変数名 => [ 条件値, チェック変数名, 固定値, TMPL変数名 ]
my %cond_fix_tbl = (
    'pg_place'  =>  [ 'P-H1',  'pg_layout',  '0', 'C_CO_PG_PLACE', ],
);
# fc_vid条件付き必須チェックテーブル
my %fc_vid_cond_tbl = (
    'av-v'  =>  [ 'other', 'av-v_velse',  'C_CO_PG_KIZAI', ],
    'av-a'  =>  [ 'other', 'av-a_velse',  'C_CO_PG_KIZAI', ],
);
# fc_pc条件付きチェックテーブル
my %fc_pc_cond_tbl = (
    'pc-v'  =>  [ 'other', 'pc-v_velse',  'C_CO_PG_KIZAI', ],
    'pc-a'  =>  [ 'other', 'pc-a_velse',  'C_CO_PG_KIZAI', ],
    'lan'   =>  [ 'other', 'pc-l_velse',  'C_CO_PG_KIZAI', ],
);

# 登録メール用変数名ハッシュ
#   key: パラメータ名
#   val: [0]:項目名
#      : [1]:undef:値使用 0:使用する/しない HASHREF:変換テーブル   
my %h_pname4mail = (
    'prog_no'       => ['企画ID', undef],
    'regdate'       => ['申し込み日付', undef],
    # 申込者情報
    'p1_name'       => ['申込者名', undef],
    'email'         => ['メールアドレス', undef],
    'reg_num'       => ['米魂番号', undef],
    'tel'           => ['電話番号', undef],
    'fax'           => ['FAX番号', undef],
    'cellphone'     => ['携帯番号', undef],
    # 企画情報
    'pg_name'       => ['企画名', undef],
    'pg_name_f'     => ['企画名ふりがな', undef],
    'pg_kind'       => ['企画種別', \%pg_kind_cnv],
    'pg_kind2'      => ['企画種別その他内容', undef],
    'pg_place'      => ['希望場所', \%pg_place_cnv],
    'pg_place2'     => ['希望場所その他内容', undef],
    'pg_layout'     => ['希望レイアウト', \%pg_layout_cnv],
    'pg_layout2'    => ['希望レイアウトその他内容', undef],
    'pg_time'       => ['希望時刻', \%pg_time_cnv],
    'pg_time2'      => ['希望時刻その他内容', undef],
    'pg_koma'       => ['希望コマ数', \%pg_koma_cnv],
    'pg_koma2'      => ['希望コマ数その他内容', undef],
    'pg_ninzu'      => ['予想人数', \%pg_ninzu_cnv],
    'pg_naiyou_k'   => ['内容事前公開', \%pg_naiyou_k_cnv],
    'pg_naiyou'     => ['企画内容', undef],
    'pg_kiroku_kb'  => ['リアルタイム公開', \%pg_kiroku_kb_cnv],
    'pg_kiroku_ka'  => ['事後公開', \%pg_kiroku_ka_cnv],
    # 使用機材
    'wbd'           => ['ホワイトボード', 0],
    'mic'           => ['壇上マイク', 0],
    'miccnt'        => ['壇上マイク本数', undef],
    'mic2'          => ['客席マイク', 0],
    'mic2cnt'       => ['客席マイク本数', undef],
    'mon'           => ['モニタ/スクリーン', 0],
    'dvd'           => ['BD/DVDプレイヤー', 0],
    'syo'           => ['書画カメラ', 0],
    'fc_other_naiyou'   => ['その他要望機材', undef],
    'fc_vid'        => ['持ち込み映像機器', \%motikomi_cnv],
    'av-v'          => ['映像機器映像接続', \%av_v_cnv],
    'av-v_velse'    => ['映像機器映像接続その他内容', undef],
    'av-a'          => ['映像機器音声接続', \%av_a_cnv],
    'av-a_velse'    => ['映像機器音声接続その他内容', undef],
    'fc_pc'         => ['持ち込みPC', \%motikomi_cnv],
    'pc-v'          => ['PC映像接続', \%pc_v_cnv],
    'pc-v_velse'    => ['PC映像接続その他内容', undef],
    'pc-a'          => ['PC音声接続', \%pc_a_cnv],
    'pc-a_velse'    => ['PC音声接続その他内容', undef],
    'lan'           => ['PC-LAN接続', \%lan_cnv],
    'pc-l_velse'    => ['PC-LAN接続その他内容', undef],
    'lanreason'     => ['LAN利用目的', undef],
    'fc_mochikomi'  => ['その他持ち込み機材', undef],
    # 企画経験
    'pg_enquete'    => ['企画経験', \%pg_enquete_cnv],
    # 重なると困る企画
    'pg_badprog'    => ['重なると困る企画', undef],
    # 出演者情報
    'youdo'         => ['申込者出演', \%ppn_youdo_cnv],
    ## 申込者以外の出演者は、Loop処理するのでプログラム埋め込み
    # 備考
    'fc_comment'    => ['備考', undef],
);

# 共通関数 HTMLテンプレート共通変数設定
sub pg_stdHtmlTmpl_set {
    my (
        $page,  # HTML::Templateオブジェクト
        $sid,   # セッションID
    ) = @_;

    $page->param(ID         => $sid)
        if ( $page->query(name => 'ID'));
    $page->param(CONNAME    => $main::CONDEF_CONST{'CONNAME'})
        if ( $page->query(name => 'CONNAME'));
    $page->param(FULLNAME   => $main::CONDEF_CONST{'FULLNAME'})
        if ( $page->query(name => 'FULLNAME'));
    $page->param(CONPERIOD  => $main::CONDEF_CONST{'CONPERIOD'})
        if ( $page->query(name => 'CONPERIOD'));
}

# 共通関数 MailBodyテンプレート共通変数設定
sub pg_stdMailTmpl_set {
    my (
        $page,      # HTML::Templateオブジェクト
        $toaddr,    # MailHeader:To
        $name,      # MailBody:申込者名
    ) = @_;
    $page->param(MIMENAME   => $main::CONDEF_CONST{'MIMENAME'})
        if ( $page->query(name => 'MIMENAME') );
    $page->param(FROMADDR   => $main::CONDEF_CONST{'ENTADDR'})
        if ( $page->query(name => 'FROMADDR') );
    $page->param(TOADDR     => $toaddr)
        if ( $page->query(name => 'TOADDR') );
    $page->param(NAME       => $name)
        if ( $page->query(name => 'NAME') );
    $page->param(FULLNAME   => $main::CONDEF_CONST{'FULLNAME'})
        if ( $page->query(name => 'FULLNAME') );
    $page->param(CONNAME    => $main::CONDEF_CONST{'CONNAME'})
        if ( $page->query(name => 'CONNAME') );
}

# 共通(ではないが、企画項目依存処理)関数 入力値チェック
sub pg_input_check {
    my (
        $page,      # HTML::Templateオブジェクト
        $cgi,       # CGIオブジェクト
    ) = @_;

    my $c_not_fill = 'bgcolor="red"';
    my %AfailVnames = ();   # エラーTMPL変数名ハッシュ(値はダミー)

    # 必須項目チェック
    while ( my ( $pname, $vname ) = each( %needs_tbl ) ) {
        if ( $cgi->param($pname) eq '' ) {
            $AfailVnames{$vname} = 1;
        }
    }
    # 条件付き必須チェック
    while ( my ( $pname, $vAprm ) = each( %cond_tbl ) ) {
        if (    ( $cgi->param($pname) eq $vAprm->[0] )
             && ( $cgi->param($vAprm->[1]) eq '' ) ) {
            $AfailVnames{$vAprm->[2]} = 1;
        }
    }
    # 条件付き値固定チェック
    while ( my ( $pname, $vAprm ) = each( %cond_fix_tbl ) ) {
        if (    ( $cgi->param($pname) eq $vAprm->[0] )
             && ( $cgi->param($vAprm->[1]) ne $vAprm->[2] ) ) {
            $AfailVnames{$vAprm->[3]} = 1;
        }
    }

    # 使用機材
    while ( my ( $pname, $vAprm ) = each( %count_tbl ) ) {
        if (    ( $cgi->param($pname) )
             && ( $cgi->param($vAprm->[0]) <= 0 ) ) {
            $AfailVnames{$vAprm->[1]} = 1;
        }
    }

    if ( $cgi->param('fc_vid') eq '0' ) {
        # 必須項目チェック
        while ( my ( $pname, $vname ) = each( %fc_vid_needs_tbl ) ) {
            if ( $cgi->param($pname) eq '' ) {
                $AfailVnames{$vname} = 1;
            }
        }
        # 条件付き必須チェック
        while ( my ( $pname, $vAprm ) = each( %fc_vid_cond_tbl ) ) {
            if (    ( $cgi->param($pname) eq $vAprm->[0] )
                 && ( $cgi->param($vAprm->[1]) eq '' ) ) {
                $AfailVnames{$vAprm->[2]} = 1;
            }
        }
    }
    if ( $cgi->param('fc_pc') eq '0' ) {
        # 必須項目チェック
        while ( my ( $pname, $vname ) = each( %fc_pc_needs_tbl ) ) {
            if ( $cgi->param($pname) eq '' ) {
                $AfailVnames{$vname} = 1;
            }
        }
        # 条件付き必須チェック
        while ( my ( $pname, $vAprm ) = each( %fc_pc_cond_tbl ) ) {
            if (    ( $cgi->param($pname) eq $vAprm->[0] )
                 && ( $cgi->param($vAprm->[1]) eq '' ) ) {
                $AfailVnames{$vAprm->[2]} = 1;
            }
        }
        # 回線理由
        if ( ( $cgi->param('lan') ne 'none' )  &&
             ( $cgi->param('lanreason') eq '' )   ) {
            $AfailVnames{'C_CO_PG_KIZAI'} = 1;
        }
    }

    # 出演者情報
    my $ppcnt;
    for ($ppcnt = 1; $ppcnt <= 8; $ppcnt++) {   # CONST: 出演者の最大値
        my $ppname      = 'pp' . $ppcnt . '_name';
        my $ppname_f    = 'pp' . $ppcnt . '_name_f';
        my $ppcon       = 'pp' . $ppcnt . '_con';
        my $ppgrq       = 'pp' . $ppcnt . '_grq';
        my $CCOPG       = 'C_CO_PG_GUEST' . $ppcnt;
        if ($cgi->param($ppname) ne '' || $cgi->param($ppname_f) ne ''){
            if ($cgi->param($ppname) eq '' || $cgi->param($ppname_f) eq '' ||
                $cgi->param($ppcon)  eq '' || $cgi->param($ppgrq) eq ''){
                $AfailVnames{$CCOPG} = 1;
            }
        }
    }
    foreach my $vname ( keys( %AfailVnames ) ) {
        $page->param($vname => $c_not_fill);
    }

    return( scalar(%AfailVnames) ? 1 : 0 );
}

# 共通関数 テンプレート変数設定
sub pg_HtmlTmpl_set {
    my (
        $page,  # HTML::Templateオブジェクト
        $sprm,  # CGI::Sessionオブジェクト
        $isMail,    # undef:HTML用 その他:Mail用
    ) = @_;

    my $pname;
    my $pAprm;

    # 単純置き換え
    foreach $pname ( @org_pname ) {
        my $value = $sprm->param($pname);
        $value =~ s/[\r\n]+/<br\/>/mg
            unless $isMail;
        $page->param( $pname => $value );
    }
    # テーブル変換(その他解釈込み)
    while ( ($pname, $pAprm) = each %tbl_pname ) {
        $page->param( $pname => cnv_radio_val($sprm, $pname, $pAprm ));
    }
    # 使用する/しない(本数解釈込み)
    while ( ($pname, $pAprm) = each %useunuse_pname ) {
        $page->param( $pname => cnv_useunuse_val($sprm, $pname, $pAprm));
    }

    my $add0 = $isMail ? "\n      利用方法:" : '<br/><b>利用方法</b>';
    my $add1 = $isMail ? "\n      " : '<div class="indent">';
    my $add2 = $isMail ? ''     : '</div>';

    # 持ち込む/持ち込まない(追加項目解釈込み)
    while ( ($pname, $pAprm) = each %motikomi_pname ) {
        my $value = $motikomi_cnv{$sprm->param($pname)};
        if ( $value eq '持ち込む' ) {
            while ( my ($pn2, $pAp2) = each %$pAprm ) {
                $value .= $add1
                        . $pAp2->[2] . ':'
                        . cnv_radio_val($sprm, $pn2, $pAp2)
                        . $add2;
            }
        }
        $page->param( $pname => $value );
    }
    # ネット接続に関する特殊処理
    if ( $motikomi_cnv{$sprm->param('fc_pc')} eq '持ち込む' ) {
        while ( ($pname, $pAprm) = each %lan_pname ) {
            my $value = cnv_radio_val($sprm, $pname, $pAprm);
            if ( $value ne '接続しない' ) {
                $value .= $add0 . $add1
                        . $sprm->param('lanreason')
                        . $add2;
            }
            $value =~ s/[\r\n]+/<br\/>/mg
                unless $isMail;
            $page->param( $pname => $value );
        }
    }

    # 出演者情報(LOOP)
    $page->param( 'youdo' => $ppn_youdo_cnv{$sprm->param('youdo')} );
    my @loop_data = ();  # TMPL変数名=>値ハッシュ参照 の配列
    my $ppcnt;
    for ($ppcnt = 1; $ppcnt <= 8; $ppcnt++) {   # CONST: 出演者の最大値
        my $prefix = 'pp' . $ppcnt;
        my $ppname = $sprm->param($prefix . '_name');
        if ( $ppname  ne '') {
            my %row_data;
            $row_data{'pp_number'}  = $ppcnt;
            $row_data{'pp_name'}    = $ppname;
            $row_data{'pp_name_f'}  = $sprm->param($prefix . '_name_f');
            $row_data{'pp_con'} = $ppn_con_cnv{$sprm->param($prefix . '_con')};
            $row_data{'pp_grq'} = $ppn_grq_cnv{$sprm->param($prefix . '_grq')};
            push(@loop_data, \%row_data);
        }
    }
    $page->param(GUEST_LOOP => \@loop_data);
}

# テーブル変換(その他解釈込み)
sub cnv_radio_val {
    my (
        $sprm,      # CGI::Sessionオブジェクト
        $pname,     # パラメータ名
        $pAprm,     # 追加情報 [0]:変換テーブル [1]:その他内容パラメータ名
    ) = @_;

    my $value = $pAprm->[0]->{$sprm->param($pname)};
    if ( ( $pAprm->[1] ne undef ) and ( $value eq 'その他' ) ) {
        $value .= '(' . $sprm->param($pAprm->[1]) . ')';
    }
    return ($value);
}

# 使用する/しない(本数解釈込み)
sub cnv_useunuse_val {
    my (
        $sprm,      # CGI::Sessionオブジェクト
        $pname,     # パラメータ名
        $opname,    # 追加情報パラメータ名 undef:なし
    ) = @_;

    my $value = $sprm->param($pname) ? '使用する' : '使用しない';
    if ( $opname && ( $value eq '使用する' ) ) {
        $value .= ' (' . $sprm->param($opname) . '本)';
    }
    return ($value);
}

# 共通関数 企画登録パラメータ生成(抽出)
#   戻り値: 連想配列参照
sub pg_createRegParam {
    my (
        $sprm,      # セッションオブジェクト(含企画パラメータ)
        $pg_num,    # 企画番号(4文字数字)
     ) = @_;
    my %reg_param = ();

    my($c_d, $c_m, $c_y) = (localtime(time))[3,4,5];
    $c_y += 1900;
    $c_m += 1;
    $sprm->param('prog_no', $pg_num);
    $sprm->param('regdate', $c_y. '/' . $c_m . '/' . $c_d);
    
    # %h_pname4mailの定義に従って値設定 
    #   key: パラメータ名
    #   val: [0]:項目名
    #      : [1]:undef:値使用 0:使用する/しない HASHREF:変換テーブル   
    while ( my ($pname, $pAval) = each(%h_pname4mail)) {
        my $val = $sprm->param($pname);
        if ( !defined($pAval->[1]) ) {
            $reg_param{$pAval->[0]} = $val
        } elsif ( $pAval->[1] eq 0 ) {
            $reg_param{$pAval->[0]} = ($val) ? '使用する' : '使用しない';
        } else {
            $reg_param{$pAval->[0]} = $pAval->[1]->{$val} || '';
        }
    }

    # 出演者情報:Loop処理なので埋め込み
    my $ppcnt;
    for ($ppcnt = 1; $ppcnt <= 8; $ppcnt++) {   # CONST: 出演者の最大値
        my $prefix = 'pp' . $ppcnt;
        if (    defined($sprm->param($prefix . '_name') )
             && ( $sprm->param($prefix . '_name') ne '' ) ) {
            $reg_param{'出演者氏名' . $ppcnt}
                = $sprm->param($prefix . '_name');
            $reg_param{'出演者氏名ふりがな' . $ppcnt}
                = $sprm->param($prefix . '_name_f');
            $reg_param{'出演交渉' . $ppcnt}
                = $ppn_con_cnv{$sprm->param($prefix . '_con')};
            $reg_param{'ゲスト申請' . $ppcnt}
                = $ppn_grq_cnv{$sprm->param($prefix . '_grq')};
        }
    }
    return(\%reg_param);
}

# 共通関数 mail送信
sub doMailSend {
    my (
        $envfrom,   # EnvelopeFrom
        $pAenvto,   # EnvelopeTo配列参照
        $body,      # メール本文
    ) = @_;

    # 開発環境では何もしない
    return if $main::CONDEF_CONST{'DEVENV'};

    my $smtp = Net::SMTP->new('127.0.0.1');
    $smtp->mail($envfrom);
    foreach my $envto ( @$pAenvto ) {
        $smtp->to($envto);
    }
    $smtp->data();
    $smtp->datasend( encode('7bit-jis', decode('utf8', $body)) );
    $smtp->dataend();
    $smtp->quit;
}

# 共通関数 テスト用 HTMLにメール内容を埋め込む
sub pg_HtmlMailChk_set {
    my (
        $page,      # HTML::Templateオブジェクト
        $mbody,     # 埋め込むメール内容 1
        $mbody2,    # 埋め込むメール内容 2
    ) = @_;
        
    $page->param(MAILPRES => '<pre>')
        if ( $page->query(name => 'MAILPRES') );
    $page->param(MAILPREE => '</pre>')
        if ( $page->query(name => 'MAILPREE') );
    $page->param(MAILHR => '<hr/>')
        if ( $page->query(name => 'MAILHR') );
    $page->param(MAILBODY => $mbody)
        if ( $page->query(name => 'MAILBODY') );
    $page->param(MAILBODY2 => $mbody2)
        if ( $page->query(name => 'MAILBODY2') );
}

1;
#--EOF--
